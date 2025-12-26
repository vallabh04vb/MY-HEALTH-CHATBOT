"""
FastAPI Backend for UHC Insurance Policy Chatbot

Integrates:
- ChromaDB for vector search
- llmops_lite for LLM management
- Input validation for edge cases
- Automatic caching and fallbacks
"""

import sys
from pathlib import Path
from typing import Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import chromadb
# ChromaDB imports handled via chromadb.PersistentClient
from datetime import datetime
from openai import OpenAI

# Add llmops_lite to path (assuming it's in parent directory)
_llmops_lite_dir = Path(__file__).parent.parent.parent.parent / "llmops_lite"
if _llmops_lite_dir.exists():
    sys.path.insert(0, str(_llmops_lite_dir))
    print(f"✅ Added llmops_lite to path: {_llmops_lite_dir}")
else:
    print(f"⚠️  Warning: llmops_lite not found at: {_llmops_lite_dir}")

try:
    from llmops_lite.llm_manager.llm import LLM as LLMOpsLLM
    from llmops_lite.llm_manager.definitions import Prompt, Payload
    from llmops_lite.specs.llm_model_specs import LLMModel
    LLMOPS_AVAILABLE = True
    print("✅ llmops_lite imported successfully")
except ImportError as e:
    print(f"❌ Error importing llmops_lite: {e}")
    LLMOPS_AVAILABLE = False

# Local imports
from app.config import settings
from app.models import (
    QueryRequest, QueryResponse, PolicySource,
    HealthResponse, ErrorResponse, FeedbackRequest, FeedbackResponse
)
from app.validators import InputValidator

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered chatbot for UHC insurance policy queries",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
llm_manager = None
fallback_llm_client = None
chroma_client = None
policy_collection = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global llm_manager, fallback_llm_client, chroma_client, policy_collection

    print("\n" + "="*80)
    print("INITIALIZING UHC INSURANCE CHATBOT API")
    print("="*80)

    # Initialize llmops_lite
    if LLMOPS_AVAILABLE:
        try:
            llm_manager = LLMOpsLLM()
            print("✅ llmops_lite LLM manager initialized")
        except Exception as e:
            print(f"❌ Error initializing llmops_lite: {e}")
            llm_manager = None
    else:
        print("⚠️  llmops_lite not available - using fallback OpenAI client")

    # Initialize fallback OpenAI client for LiteLLM proxy
    if not llm_manager and settings.LITELLM_PROXY_BASE_URL:
        try:
            fallback_llm_client = OpenAI(
                api_key=settings.LITELLM_PROXY_SECRET_KEY,
                base_url=settings.LITELLM_PROXY_BASE_URL
            )
            print(f"✅ Fallback LLM client initialized (LiteLLM proxy)")
        except Exception as e:
            print(f"❌ Error initializing fallback LLM client: {e}")
            fallback_llm_client = None

    # Initialize ChromaDB
    try:
        # Use new ChromaDB 1.x API
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

        policy_collection = chroma_client.get_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )

        doc_count = policy_collection.count()
        print(f"✅ ChromaDB initialized: {doc_count} documents in collection")

        if doc_count == 0:
            print("⚠️  Warning: ChromaDB collection is empty!")
            print("   Run data_pipeline/load_chromadb.py to load policies")

    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        chroma_client = None
        policy_collection = None

    print("="*80 + "\n")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "UHC Insurance Policy Chatbot API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Health check endpoint for monitoring"""

    # Check ChromaDB
    chroma_collections = 0
    if chroma_client:
        try:
            chroma_collections = len(chroma_client.list_collections())
        except:
            pass

    # Get LLM proxy URL
    llm_proxy = settings.LITELLM_PROXY_BASE_URL or "Not configured"

    return HealthResponse(
        status="healthy" if policy_collection else "degraded",
        version=settings.APP_VERSION,
        llm_proxy=llm_proxy,
        chroma_collections=chroma_collections
    )

@app.get("/api/providers", tags=["Query"])
async def get_providers():
    """
    Get list of available insurance providers dynamically from ChromaDB.
    This ensures frontend automatically shows new providers without code changes.
    """
    if not policy_collection:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ChromaDB not initialized"
        )

    try:
        # Get all documents to extract unique providers
        results = policy_collection.get()

        # Extract unique providers from metadata
        providers_set = set()
        provider_info = {}

        if results and results.get('metadatas'):
            for metadata in results['metadatas']:
                provider = metadata.get('provider')
                if provider:
                    providers_set.add(provider)
                    # Store display name mapping
                    if provider not in provider_info:
                        provider_info[provider] = {
                            'value': provider,
                            'label': provider,
                            'display_name': metadata.get('provider', provider)
                        }

        # Convert to sorted list
        providers_list = sorted([
            provider_info[p] for p in providers_set
        ], key=lambda x: x['value'])

        return {
            "providers": providers_list,
            "count": len(providers_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching providers: {str(e)}"
        )

@app.post("/api/ask", response_model=QueryResponse, tags=["Query"])
async def ask_question(request: QueryRequest):
    """
    Main endpoint: Answer insurance policy questions

    Process:
    1. Validate and sanitize input
    2. Retrieve relevant policy chunks from ChromaDB
    3. Generate answer using llmops_lite
    4. Return answer with source citations
    """

    # Check if services are available
    if not policy_collection:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ChromaDB not available. Please check configuration."
        )

    if not llm_manager and not fallback_llm_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Please check LLM configuration."
        )

    try:
        # === STEP 1: VALIDATE INPUT ===
        try:
            validated = InputValidator.validate_and_prepare(
                request.question,
                request.provider
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        question = validated['question']
        provider = validated['provider']
        is_relevant = validated['is_relevant']
        relevance_score = validated['relevance_score']

        # EDGE CASE: Non-medical question
        if not is_relevant:
            return QueryResponse(
                answer=(
                    "I can only answer questions about UHC insurance policies and medical coverage. "
                    "Please ask about procedures, coverage criteria, or claim denials."
                ),
                sources=[],
                confidence=0.0,
                provider=provider,
                cached=False
            )

        # === STEP 2: RETRIEVE FROM CHROMADB ===
        try:
            results = policy_collection.query(
                query_texts=[question],
                n_results=settings.TOP_K_RESULTS,
                where={"provider": provider}  # Filter by provider
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vector search error: {str(e)}"
            )

        # EDGE CASE: No relevant policies found
        if not results['documents'] or len(results['documents'][0]) == 0:
            return QueryResponse(
                answer=(
                    f"I couldn't find relevant {provider} policies for your question. "
                    "Please try rephrasing or contact UHC directly for clarification."
                ),
                sources=[],
                confidence=0.0,
                provider=provider,
                cached=False
            )

        # === STEP 3: FORMAT CONTEXT ===
        context_chunks = results['documents'][0]
        context = "\n\n".join([
            f"Policy Excerpt {i+1}:\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        # Extract sources
        sources = [
            PolicySource(
                policy_id=meta.get('policy_id', 'unknown'),
                title=meta.get('title', 'Unknown Policy'),
                url=meta.get('source_url', ''),
                excerpt=doc[:200] + "..." if len(doc) > 200 else doc
            )
            for meta, doc in zip(results['metadatas'][0], results['documents'][0])
        ]

        # === STEP 4: CREATE PROMPT ===
        prompt_template = f"""You are an expert medical billing assistant specializing in insurance policies.

Context from {provider} Policies:
{context}

Doctor's Question: {question}

Instructions:
1. Answer ONLY based on the provided policy excerpts
2. If the policy is unclear, say "The policy doesn't provide clear guidance on this"
3. Cite specific policy sections when possible
4. Use professional medical billing terminology
5. If the question can't be answered from the context, say "I don't have enough information from {provider} policies to answer this"
6. Keep your answer concise and actionable

Answer:"""

        # === STEP 5: EXECUTE LLM REQUEST ===
        try:
            if llm_manager:
                # Use llmops_lite if available
                insurance_prompt = Prompt(
                    name="insurance_qa",
                    description=f"Answer question about {provider} insurance policies",
                    template=prompt_template
                )

                model_config = LLMModel.GPT_4O_MINI

                payload = Payload(
                    prompt=insurance_prompt,
                    model=model_config.model_name,
                    temperature=settings.DEFAULT_TEMPERATURE,
                    datapoint_id=f"query_{hash(question)}",
                    vars={"context": context, "question": question},
                    extra_args={
                        **model_config.extra_args,
                        "max_tokens": settings.MAX_TOKENS,
                        "process_output": False
                    }
                )

                response = llm_manager.execute_llm_prompt(
                    payload,
                    use_cache=settings.ENABLE_CACHE
                )

                if hasattr(response, 'choices') and len(response.choices) > 0:
                    answer = response.choices[0].message.content
                else:
                    answer = str(response)

            else:
                # Use fallback OpenAI client
                response = fallback_llm_client.chat.completions.create(
                    model=settings.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert medical billing assistant."},
                        {"role": "user", "content": prompt_template}
                    ],
                    temperature=settings.DEFAULT_TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )

                answer = response.choices[0].message.content

            cached = False

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LLM execution error: {str(e)}"
            )

        # === STEP 6: CALCULATE CONFIDENCE ===
        confidence = calculate_confidence(answer, context_chunks)

        # EDGE CASE: Low confidence answer
        if confidence < settings.LOW_CONFIDENCE_THRESHOLD:
            answer += (
                "\n\n⚠️ Note: I have low confidence in this answer. "
                "Please verify this information with UHC directly or consult the policy documents."
            )

        # === STEP 7: RETURN RESPONSE ===
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            provider=provider,
            cached=cached
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback on chatbot responses

    This can be used to improve the system over time
    """
    # In production, save feedback to database for analysis
    # For now, just acknowledge receipt

    print(f"\nFeedback received:")
    print(f"  Question: {request.question[:50]}...")
    print(f"  Rating: {request.rating}/5")
    print(f"  Comment: {request.comment}")

    return FeedbackResponse(
        success=True,
        message="Thank you for your feedback! We'll use it to improve the chatbot."
    )

# Helper functions

def calculate_confidence(answer: str, context_chunks: List[str]) -> float:
    """
    Calculate confidence score based on answer-context alignment

    Simple heuristic: check if key terms from answer appear in context
    """
    # Extract important words from answer (skip common words)
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'for', 'to', 'of',
        'and', 'or', 'but', 'in', 'on', 'at', 'from', 'by', 'with', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }

    answer_words = set(answer.lower().split()) - stop_words

    # Count how many answer words appear in context
    context_text = " ".join(context_chunks).lower()
    matches = sum(1 for word in answer_words if len(word) > 3 and word in context_text)

    # Calculate confidence (max 1.0)
    confidence = min(matches / max(len(answer_words), 1), 1.0) if answer_words else 0.5

    # Boost confidence if specific medical terms are present
    medical_terms_in_answer = sum(
        1 for word in answer_words
        if word in InputValidator.MEDICAL_KEYWORDS
    )

    if medical_terms_in_answer > 0:
        confidence = min(confidence * 1.2, 1.0)

    return round(confidence, 2)

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    print(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc) if settings.DEBUG else None,
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
