from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from core.state import OrganismState
from human_interface.chat_engine import ChatEngine
from core.pulse_schema import PulseSchema
from core.intelligence_categories import INTELLIGENCE_CATEGORIES
from cognitive_kernel.tools.web_search_tool import WebSearchTool
from cognitive_kernel.local_llm_client import LocalLLMClient
from cognitive_kernel.gemini_client import GeminiClient
import json
import uuid
import time
import zipfile
import io

app = FastAPI(title="BIZIT Chat API - Minimal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize with minimal dependencies
state_manager = OrganismState()
llm_client = LocalLLMClient()
gemini_client = GeminiClient(model_name="gemini-1.5-pro") 
search_tool = WebSearchTool()

# Mock GraphManager to avoid Neo4j dependency
class MockGraphManager:
    def __init__(self): pass

chat_engine = ChatEngine(MockGraphManager(), state_manager)

@app.get("/")
async def root():
    return {"status": "Chat API Online", "endpoints": ["/chat", "/search", "/status", "/persona", "/outcome"]}

@app.post("/chat")
async def chat(data: dict):
    """Streaming chat endpoint"""
    state_manager.load_state()
    
    async def event_generator():
        async for chunk in chat_engine.process_query_stream(data.get("query", "")):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")

import asyncio

@app.post("/search")
async def search(data: dict):
    """Deep Intelligence Search Endpoint with Dynamic Grounding & Clarity Loop"""
    print(f"[SEARCH_REQUEST] Received: {data}")
    query = data.get("query", "")
    if not query:
        return {"status": "error", "message": "Empty query"}
    
    # 1. Strategy Inference
    print("[STRATEGY] Inferring Strategic Mandate...")
    strategy_prompt = f"Classify this query into ONE mandate: PRESERVE, GROWTH, or ARBITRAGE.\nQuery: \"{query}\"\nRespond with ONLY the name."
    try:
        strategy_raw = await asyncio.wait_for(llm_client.generate(strategy_prompt), timeout=15.0)
        strategy = strategy_raw.strip().upper()
        if strategy not in ["PRESERVE", "GROWTH", "ARBITRAGE"]: strategy = "GROWTH"
    except: strategy = "GROWTH"

    # 1.1 Query Type Classification (Dynamic Response Format)
    print("[CLASSIFICATION] Determining Query Type...")
    type_prompt = f"""Classify this query into ONE type:
    - FACTUAL: Simple fact lookup (e.g., "What is the NGN rate?")
    - STRATEGIC: Complex decision requiring forecast/recommendations (e.g., "Should I expand?")
    - COMPARATIVE: Side-by-side comparison (e.g., "Lagos vs Abuja market")
    
    Query: "{query}"
    Respond with ONLY: FACTUAL, STRATEGIC, or COMPARATIVE"""
    
    try:
        query_type_raw = await asyncio.wait_for(llm_client.generate(type_prompt), timeout=10.0)
        query_type = query_type_raw.strip().upper()
        if query_type not in ["FACTUAL", "STRATEGIC", "COMPARATIVE"]: query_type = "STRATEGIC"
    except: query_type = "STRATEGIC"
    
    print(f"[CLASSIFICATION] Query Type: {query_type}")
    
    # 1.1.1 Response Format Detection (Dynamic Responses)
    if query_type == "FACTUAL":
        response_format = "CONVERSATIONAL"  # Plain text, no JSON
    elif query_type == "COMPARATIVE":
        response_format = "TABULAR"  # Markdown table
    else:
        response_format = "STRUCTURED"  # Full JSON schema
    
    print(f"[FORMAT] Response Format: {response_format}")

    # 1.2 Category Inference
    active_categories = ["RISK", "FORECAST"] # Universal Layers
    try:
        cat_prompt = f"Identify relevant intelligence layers (MACRO, PRODUCT, SME, etc) for: \"{query}\"\nRespond with COMMA-SEPARATED KEYS."
        cat_raw = await asyncio.wait_for(gemini_client.generate(cat_prompt), timeout=15.0)
        for k in [x.strip().upper() for x in cat_raw.split(",")]:
            if k in INTELLIGENCE_CATEGORIES and k not in active_categories:
                active_categories.append(k)
    except: active_categories = ["MACRO", "SME", "RISK", "FORECAST"]

    # 1.3 Search Intent Detection (Smart Context Routing)
    print("[ROUTING] Detecting search intent...")
    docs = state_manager.documents
    doc_keywords = ["my", "uploaded", "document", "file", "invoice", "report", "statement"]
    doc_filenames = [d['filename'].lower() for d in docs] if docs else []
    
    # Check if query references uploaded documents
    query_lower = query.lower()
    references_docs = (
        any(keyword in query_lower for keyword in doc_keywords) or
        any(filename in query_lower for filename in doc_filenames)
    )
    
    # Check if query needs real-time/external data
    external_keywords = ["current", "latest", "today", "now", "rate", "price", "market", "news", "trend"]
    needs_external = any(keyword in query_lower for keyword in external_keywords)
    
    # Determine search mode
    if references_docs and not needs_external:
        search_mode = "INTERNAL"  # Only uploaded docs
        print(f"[ROUTING] Mode: INTERNAL (uploaded documents only)")
    elif needs_external and not references_docs:
        search_mode = "EXTERNAL"  # Only web search
        print(f"[ROUTING] Mode: EXTERNAL (web sources only)")
    else:
        search_mode = "HYBRID"  # Both sources
        print(f"[ROUTING] Mode: HYBRID (web + documents)")

    # 1.2 Interactive Clarity Check & Dynamic Grounding
    dynamic_state = state_manager.get_dynamic_state()
    user_clarification = data.get("clarification", "")

    if not user_clarification:
        clarity_prompt = f"""
        Analyze if this query matches the user's business persona or if it requires interactive clarification.
        Persona Sector: {dynamic_state['persona'].get('sector')}
        Persona Goals: {', '.join(dynamic_state['persona'].get('growth_goals', []))}
        Query: "{query}"
        
        If there is a mismatch (e.g. Fashion asking about Tech) or intent ambiguity, respond with JSON:
        {{"required": true, "question": "The question to ask user.", "options": ["Option 1", "Option 2"]}}
        Else: {{"required": false}}
        """
        try:
            clarity_raw = await gemini_client.generate_reasoning(clarity_prompt, thinking_level="TACTICAL")
            if clarity_raw.get("required"):
                return {
                    "status": "CLARITY_REQUIRED",
                    "question": clarity_raw["question"],
                    "options": clarity_raw.get("options", ["Pivot Intent", "Strategic Synergy", "Simple Interest"]),
                    "context": dynamic_state
                }
        except: pass

    # Prepare Rich Grounding Context
    vitals = dynamic_state['vitals']
    grounding_context = f"""
    DYNAMIC_BUSINESS_TWIN_STATE:
    - Persona: {dynamic_state['persona'].get('sector')} in {dynamic_state['persona'].get('hq')}
    - Mandates: {', '.join(dynamic_state['persona'].get('growth_goals', []))}
    - Liquidity: ${vitals['liquid_cash']:,.2f}
    - Performance: {vitals['recent_sales_24h']} sales (24h)
    - Intent Alignment: {user_clarification or "Aligned with Persona"}
    """

    # 2. Multi-Source Gathering (Context-Routed)
    print(f"[SEARCH] Gathering Intelligence for: '{query}' (Mode: {search_mode})")
    
    # 2.1 Web Search (if needed)
    results_list = []
    if search_mode in ["EXTERNAL", "HYBRID"]:
        try:
            search_results = search_tool.execute(query=query)
            results_list = search_results.get('results', [])
            print(f"[SEARCH] Retrieved {len(results_list)} web sources")
        except Exception as e:
            print(f"[SEARCH] Web search failed: {e}")
            results_list = []
    else:
        print("[SEARCH] Skipping web search (INTERNAL mode)")

    # 2.2 Document Crossover (if needed)
    doc_context = ""
    doc_count = 0
    if search_mode in ["INTERNAL", "HYBRID"] and state_manager.documents:
        doc_summaries = [f"[{d['filename']}]: {d['intelligence_summary']}" for d in state_manager.documents]
        doc_context = "\n".join(doc_summaries)
        doc_count = len(state_manager.documents)
        print(f"[SEARCH] Including {doc_count} uploaded documents")
    else:
        print("[SEARCH] Skipping document context (EXTERNAL mode or no docs)")

    # 3. Deep Synthesis (Format-Adaptive)
    theme_directives = "\n".join([f"- {k}: {INTELLIGENCE_CATEGORIES[k].get('directive','')}" for k in active_categories if k in INTELLIGENCE_CATEGORIES])
    results_context = json.dumps(results_list)[:8000]
    
    # Format-Based Synthesis
    if response_format == "CONVERSATIONAL":
        # Plain text response for factual queries
        synthesis_prompt = f"""As BIZIT Sovereign Intelligence, answer this question conversationally.
        {grounding_context}
        
        Query: "{query}"
        Search Results: {results_context}
        Document Context: {doc_context if doc_context else "No uploaded documents."}
        
        Provide a direct, conversational answer in 2-4 sentences. Be specific and cite sources naturally.
        Do NOT use JSON. Just answer the question naturally."""
        
        try:
            synthesis_raw = await asyncio.wait_for(gemini_client.generate(synthesis_prompt), timeout=60.0)
            # Return conversational format
            return {
                "status": "success",
                "format": "conversational",
                "answer": synthesis_raw,
                "search_mode": search_mode,
                "doc_count": doc_count,
                "web_source_count": len(results_list)
            }
        except Exception as e:
            print(f"[SYNTHESIS] Error: {e}")
            return {"status": "error", "message": str(e)}
    
    elif response_format == "TABULAR":
        # Markdown table for comparative queries
        synthesis_prompt = f"""As BIZIT Sovereign Intelligence, create a comparison table.
        {grounding_context}
        
        Query: "{query}"
        Search Results: {results_context}
        Document Context: {doc_context if doc_context else "No uploaded documents."}
        
        Create a markdown table comparing the options. Include columns for key factors.
        After the table, provide a 1-sentence recommendation.
        
        Format:
        | Option | Factor 1 | Factor 2 | Score |
        |--------|----------|----------|-------|
        | ...    | ...      | ...      | ...   |
        
        Recommendation: [Your recommendation]"""
        
        try:
            synthesis_raw = await asyncio.wait_for(gemini_client.generate(synthesis_prompt), timeout=60.0)
            # Return tabular format
            return {
                "status": "success",
                "format": "tabular",
                "table": synthesis_raw,
                "search_mode": search_mode,
                "doc_count": doc_count,
                "web_source_count": len(results_list)
            }
        except Exception as e:
            print(f"[SYNTHESIS] Error: {e}")
            return {"status": "error", "message": str(e)}
    
    else:  # STRUCTURED format (current approach)
        synthesis_prompt = f"""
        As BIZIT Sovereign Intelligence, synthesize this report for strategy: {strategy}.
        {grounding_context}
        
        Active Intelligence Layers:
        {theme_directives}
        
        INGESTED BUSINESS DOCUMENTS:
        {doc_context if doc_context else "No private docs."}
        
        Query: "{query}"
        Search Results: {results_context}
        
        Respond ONLY with a valid JSON object following the Sovereign Pulse Schema.
        """
    
    try:
        synthesis = await asyncio.wait_for(gemini_client.generate_reasoning(synthesis_prompt, thinking_level="SOVEREIGN"), timeout=90.0)
    except Exception as e:
        print(f"[SYNTHESIS] Error: {e}")
        synthesis = {"headline": "Synthesis Core Error", "signal": str(e), "urgency": "WATCH", "impact": "None", "confidence": 0.0, "forecast": [], "recommendations": [], "sources": []}

    brief = PulseSchema.create_pulse_card(
        headline=synthesis.get("headline", "Signal Detected"),
        urgency=synthesis.get("urgency", "WATCH"),
        signal=synthesis.get("signal", "No data."),
        impact=synthesis.get("impact", "Unknown."),
        trust_hash=f"ipfs://{hash(query)}"
    )
    brief.update({
        "confidence": synthesis.get("confidence", 0.5),
        "sources": synthesis.get("sources", []),
        "forecast": synthesis.get("forecast", []),
        "recommendations": synthesis.get("recommendations", []),
        "search_mode": search_mode,  # EXTERNAL, INTERNAL, or HYBRID
        "doc_count": doc_count,  # Number of uploaded docs used
        "web_source_count": len(results_list)  # Number of web sources used
    })
    
    return {"status": "success", "brief": brief, "strategy": strategy}

def _generate_heuristic_summary(filename: str, content: str, extension: str) -> str:
    """Generates a deterministic summary based on file content when LLMs fail."""
    if extension in ["xlsx", "xls"]:
        lines = content.split("\n")
        # Extract headers or first valid data rows
        data_preview = "\n".join(lines[:10])
        return f"HEURISTIC_ANALYSIS: Excel Spreadsheet '{filename}'. Found data structures including:\n{data_preview}\n[Manual Inspection Recommended]"
    elif extension in ["txt", "csv", "json"]:
        preview = content[:500].replace("\n", " ")
        return f"HEURISTIC_ANALYSIS: Text-based document '{filename}'. Content Preview: {preview}..."
    else:
        return f"HEURISTIC_ANALYSIS: Metadata extraction for '{filename}'. Format: {extension.upper()}. [Automated summary unavailable]"

async def _process_single_file(filename: str, raw_data: bytes):
    """Helper to digest a single file and return its doc_entry."""
    print(f"[DEBUG] Processing {filename} (Size: {len(raw_data)} bytes)")
    extension = filename.split(".")[-1].lower()
    content = ""
    analysis = ""
    
    if extension in ["txt", "csv", "json"]:
        content = raw_data.decode("utf-8")
        summary_prompt = f"Analyze this business document and extract key strategic signals, financial vitals, or risk factors. Format as a concise intelligence brief.\n\nDocument Content:\n{content[:5000]}"
        analysis = await gemini_client.generate(summary_prompt)
    elif extension in ["jpg", "jpeg", "png", "webp"]:
        # Visual Ingestion Path
        visual_prompt = "Analyze this business image (Receipt/Dashboard/Statement). Extract key strategic signals, amounts, dates, and vendor names. Format as a concise intelligence brief."
        mime_type = f"image/{extension if extension != 'jpg' else 'jpeg'}"
        analysis = await gemini_client.generate_multimodal(visual_prompt, raw_data, mime_type)
        content = f"[VISUAL DATA INGESTED FROM {filename}]"
    elif extension in ["mp3", "wav", "m4a"]:
        # Audio Ingestion Path
        audio_prompt = "Listen to this business audio (Voice Note/Meeting/Call). Extract strategic commitments, price signals, sentiment, and action items. Format as a concise intelligence brief."
        mime_type = "audio/mpeg" if extension == "mp3" else f"audio/{extension}"
        if extension == "m4a": mime_type = "audio/mp4"
        analysis = await gemini_client.generate_multimodal(audio_prompt, raw_data, mime_type)
        content = f"[AUDIO DATA INGESTED FROM {filename}]"
    elif extension in ["xlsx", "xls"]:
        # Excel Ingestion Path
        try:
            from openpyxl import load_workbook
            import io
            
            # Load workbook from bytes
            wb = load_workbook(io.BytesIO(raw_data), data_only=True)
            sheet_names = wb.sheetnames
            
            # Extract data from first sheet (or all sheets if small)
            excel_data = []
            for sheet_name in sheet_names[:3]:  # Max 3 sheets
                ws = wb[sheet_name]
                # Get first 20 rows of data
                rows = []
                for idx, row in enumerate(ws.iter_rows(values_only=True)):
                    if idx >= 20: break
                    rows.append(row)
                excel_data.append(f"Sheet: {sheet_name}\n" + "\n".join([str(r) for r in rows if any(r)]))
            
            content = "\n\n".join(excel_data)
            print(f"[DEBUG] {filename}: Extracted {len(content)} chars of data from {len(sheet_names)} sheets.")
            
            # Analyze Excel content
            excel_prompt = f"Analyze this Excel spreadsheet data. Extract key business metrics, financial data, trends, and strategic insights. Format as a concise intelligence brief.\n\nFilename: {filename}\nSheets: {', '.join(sheet_names)}\n\nData Preview:\n{content[:3000]}"
            analysis = await gemini_client.generate(excel_prompt)
            print(f"[DEBUG] {filename}: Gemini generated {len(analysis)} chars of analysis.")
        except Exception as e:
            content = f"[EXCEL PROCESSING ERROR: {str(e)}]"
            analysis = f"Excel file detected ({filename}) but processing failed: {str(e)}"
    elif extension == "pdf":
        content = f"[PDF CONTENT EXTRACTED FROM {filename}]" 
        analysis = await gemini_client.generate(f"Summarize the likely strategic content of this business PDF filename: {filename}")
    elif extension in ["doc", "docx"]:
        content = f"[DOCX CONTENT EXTRACTED FROM {filename}]"
        analysis = await gemini_client.generate(f"Summarize the likely strategic content of this business DOCX filename: {filename}")
    else:
        content = f"[UNSUPPORTED FORMAT: {extension}]"
        analysis = "Unsupported file format analysis unavailable."

    # Multi-Tier Fallback Logic for Analysis
    if not analysis or "error" in analysis.lower() or "unsupported" in analysis.lower():
        print(f"[FALLBACK] Gemini failed for {filename}. Attempting Local LLM...")
        try:
            local_prompt = f"Summarize this business data briefly: {content[:2000]}"
            analysis = await llm_client.generate(local_prompt)
            if "offline" in analysis.lower() or not analysis:
                raise Exception("Local LLM Offline")
        except:
            print(f"[FALLBACK] Local LLM failed for {filename}. Using Heuristics...")
            analysis = _generate_heuristic_summary(filename, content, extension)

    return {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "type": extension,
        "timestamp": time.time(),
        "raw_preview": content[:1000],
        "intelligence_summary": analysis
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Ingests documents or archives into the Sovereign Kernel."""
    print(f"[INGESTION] Received: {file.filename}")
    
    try:
        raw_data = await file.read()
        extension = file.filename.split(".")[-1].lower()
        
        if extension == "zip":
            # Batch Ingestion Path
            print(f"[INGESTION] Processing ZIP Archive: {file.filename}")
            extracted_entries = []
            with zipfile.ZipFile(io.BytesIO(raw_data)) as z:
                for z_name in z.namelist():
                    if z_name.endswith("/") or "__MACOSX" in z_name: continue
                    print(f"  -> Extracting: {z_name}")
                    with z.open(z_name) as z_file:
                        z_data = z_file.read()
                        entry = await _process_single_file(z_name, z_data)
                        state_manager.add_document(entry)
                        extracted_entries.append(entry)
            
            # Collective Intelligence Summary
            if extracted_entries:
                patterns = "\n".join([f"- {e['filename']}: {e['intelligence_summary']}" for e in extracted_entries[:10]])
                collective_prompt = f"Analyze these extracted business signals and identify cross-file strategic patterns, unified risk factors, or financial discrepancies across this batch.\n\nSignals:\n{patterns}"
                collective_summary = await gemini_client.generate(collective_prompt)
                
                # Generate Suggested Queries
                suggestions_prompt = f"Based on these uploaded documents, suggest 3 specific, actionable search queries the user should run. Format as a JSON array of strings.\n\nDocument Summaries:\n{patterns}"
                try:
                    suggestions_raw = await gemini_client.generate(suggestions_prompt)
                    # Try to parse as JSON array
                    import re
                    json_match = re.search(r'\[.*\]', suggestions_raw, re.DOTALL)
                    if json_match:
                        suggested_queries = json.loads(json_match.group())
                    else:
                        # Fallback: split by newlines
                        suggested_queries = [line.strip('- ').strip() for line in suggestions_raw.split('\n') if line.strip()][:3]
                except:
                    suggested_queries = [
                        f"Analyze pricing trends across {len(extracted_entries)} files",
                        "Identify risk factors in uploaded documents",
                        "Compare financial vitals across batch"
                    ]
            else:
                collective_summary = "Zip archive was empty or contained no compatible files."
                suggested_queries = []
            
            print(f"[INGESTION] Processed ZIP Batch: {len(extracted_entries)} files.")
            return {
                "status": "success", 
                "filename": file.filename, 
                "batch_size": len(extracted_entries),
                "summary": collective_summary,
                "suggested_queries": suggested_queries
            }
        else:
            # Single File Ingestion Path
            entry = await _process_single_file(file.filename, raw_data)
            state_manager.add_document(entry)
            print(f"[INGESTION] Processed {file.filename} (Multimodal: {entry['type'] in ['jpg', 'png', 'webp', 'jpeg', 'mp3', 'wav', 'm4a']}) successfully.")
            
            # Generate suggested queries for single file
            suggestions_prompt = f"Based on this uploaded document, suggest 3 specific, actionable search queries the user should run. Format as a JSON array of strings.\n\nDocument: {entry['filename']}\nSummary: {entry['intelligence_summary']}"
            try:
                suggestions_raw = await gemini_client.generate(suggestions_prompt)
                import re
                json_match = re.search(r'\[.*\]', suggestions_raw, re.DOTALL)
                if json_match:
                    suggested_queries = json.loads(json_match.group())
                else:
                    suggested_queries = [line.strip('- ').strip() for line in suggestions_raw.split('\n') if line.strip()][:3]
            except:
                suggested_queries = [
                    f"Analyze key insights from {entry['filename']}",
                    "Identify risk factors in this document",
                    "Extract financial vitals and pricing signals"
                ]
            
            return {
                "status": "success", 
                "filename": file.filename,
                "batch_size": 1,
                "summary": entry["intelligence_summary"],
                "suggested_queries": suggested_queries
            }
            
    except Exception as e:
        print(f"[INGESTION] Failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/persona")
async def get_persona():
    """Returns the Sovereign Business Persona."""
    return state_manager.persona

@app.post("/persona")
async def update_persona(persona: Dict[str, Any]):
    """Updates the Sovereign Business Persona."""
    state_manager.update_persona(persona)
    return {"status": "success", "persona": state_manager.persona}

@app.post("/outcome")
async def record_outcome(feedback: Dict[str, Any]):
    """Records real-world outcome of strategic recommendations."""
    feedback_entry = {
        "timestamp": time.time(),
        **feedback
    }
    state_manager.add_feedback(feedback_entry)
    print(f"[OUTCOME] Verified Result: {feedback.get('result', 'UNKNOWN')}")
    return {"status": "accepted", "weisman_bonus": 0.01}

@app.get("/briefs")
async def get_briefs():
    """Returns real intelligence briefs from the organism state"""
    state_manager.load_state()
    return []

@app.post("/documents/query")
async def query_documents(data: Dict[str, Any]):
    """Interactive document querying with conversation history."""
    query = data.get("query", "")
    doc_ids = data.get("doc_ids", [])  # Specific docs to query (empty = all)
    history = data.get("history", [])  # Previous Q&A for context
    
    if not query:
        return {"status": "error", "message": "Query is required"}
    
    # Get selected documents
    if doc_ids:
        docs = [state_manager.get_document(doc_id) for doc_id in doc_ids]
        docs = [d for d in docs if d is not None]  # Filter out None
    else:
        docs = state_manager.documents  # All docs
    
    if not docs:
        return {"status": "error", "message": "No documents found"}
    
    # Build context from documents
    doc_context = "\n\n".join([
        f"Document: {d['filename']}\nType: {d['type']}\nSummary: {d['intelligence_summary']}"
        for d in docs
    ])
    
    # Include conversation history for context
    history_context = ""
    if history:
        history_context = "Previous Conversation:\n" + "\n".join([
            f"Q: {h.get('query', '')}\nA: {h.get('answer', '')}"
            for h in history[-3:]  # Last 3 exchanges
        ])
    
    # Query with full context
    prompt = f"""Based on these uploaded documents, answer the question conversationally.

{history_context}

Documents:
{doc_context}

Question: {query}

Provide a direct, conversational answer. Cite specific documents when relevant (e.g., "According to invoice_jan.pdf...").
Be specific with numbers, dates, and details from the documents."""
    
    try:
        # Tier 1: Gemini
        answer = await asyncio.wait_for(gemini_client.generate(prompt), timeout=30.0)
        
        if not answer or len(answer) < 5:
            raise Exception("Gemini Empty Response")
            
    except Exception as e:
        print(f"[QUERY_FALLBACK] Gemini Error: {e}. Attempting Local LLM...")
        try:
            # Tier 2: Local LLM
            answer = await asyncio.wait_for(llm_client.generate(prompt), timeout=45.0)
            if "offline" in answer.lower():
                raise Exception("Local LLM Offline")
        except Exception as e2:
            print(f"[QUERY_FALLBACK] Local LLM Error: {e2}. Using Heuristic Keyword Search...")
            # Tier 3: Heuristic Keyword Search
            keywords = [w.lower() for w in query.split() if len(w) > 3]
            matches = []
            for d in docs:
                file_content = d.get("raw_preview", "").lower()
                if any(k in file_content for k in keywords):
                    matches.append(f"Match in {d['filename']}: {d['raw_preview'][:300]}")
            
            if matches:
                answer = "⚠️ [LOCAL_HEURISTIC_MODE]: I couldn't reach the AI, but I found these relevant parts in your documents:\n\n" + "\n\n".join(matches)
            else:
                answer = "⚠️ [OFFLINE]: I couldn't reach any AI models and found no direct keyword matches for your query."

    return {
            "status": "success",
            "answer": answer,
            "doc_count": len(docs),
            "cited_docs": [d['filename'] for d in docs],
            "query": query
        }
    except Exception as e:
        print(f"[DOC_QUERY] Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/documents")
async def list_documents():
    """Returns all uploaded documents with metadata."""
    docs = state_manager.documents
    return {
        "total": len(docs),
        "documents": [{
            "id": d["id"],
            "filename": d["filename"],
            "type": d["type"],
            "timestamp": d["timestamp"],
            "summary": d["intelligence_summary"][:200] + "..." if len(d["intelligence_summary"]) > 200 else d["intelligence_summary"]
        } for d in docs]
    }

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Removes a document from the knowledge base."""
    doc = state_manager.get_document(doc_id)
    if not doc:
        return {"status": "error", "message": "Document not found"}
    
    state_manager.memory_documents = [d for d in state_manager.documents if d["id"] != doc_id]
    state_manager.save_state()
    
    return {"status": "deleted", "id": doc_id, "filename": doc.get("filename")}

@app.get("/status")
async def get_status():
    return {
        "organism_status": "active",
        "level": 34,
        "weisman_score": state_manager.get_weisman_score(),
        "doc_count": len(state_manager.documents)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
