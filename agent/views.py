import json
import threading
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Document, ChatHistory, Chunk

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# === Asynchronous (simulated) document processing ===
def async_process_document(doc, doc_url):
    try:
        # 1. Scrape and clean (very basic)
        if not BeautifulSoup:
            doc.status = "failed"
            doc.error_message = "BeautifulSoup not installed"
            doc.save()
            return

        response = requests.get(doc_url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)

        # 2. Chunking (simple: by paragraph lines)
        paragraphs = [p.strip() for p in text_content.split("\n") if p.strip()]
        all_chunks = []
        for para in paragraphs:
            if len(para) > 40:  # avoid tiny fragments
                all_chunks.append(para[:2000])  # limit chunk size

        # 3. Store chunks (without embeddings for now)
        for chunk_text in all_chunks:
            Chunk.objects.create(document=doc, text=chunk_text)

        doc.status = "processed"
        doc.save()
    except Exception as e:
        doc.status = "failed"
        doc.save()

@csrf_exempt
def process_documentation(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Método no permitido"}, status=405)
        chat_id = request.POST.get("chatId")
        doc_url = request.POST.get("doc_url")
        if not chat_id or not doc_url:
            return JsonResponse({"error": "Falta chatId o doc_url"}, status=400)

        doc, created = Document.objects.get_or_create(
            chat_id=chat_id,
            defaults={"url": doc_url, "status": "processing"},
        )
        if not created:
            doc.status = "processing"
            doc.url = doc_url
            doc.save()
            Chunk.objects.filter(document=doc).delete()

        threading.Thread(target=async_process_document, args=(doc, doc_url)).start()
        return JsonResponse({"status": doc.status, "chat_id": chat_id})

    except Exception as e:
        # Siempre responde con JSON, incluso en error
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

def processing_status(request, chat_id):
    doc = Document.objects.filter(chat_id=chat_id).first()
    if not doc:
        return JsonResponse({"error": "No existe ese chatId"}, status=404)
    return JsonResponse({"status": doc.status})

@csrf_exempt
def chat_view(request, chat_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        question = data.get("question", "")
        if not question.strip():
            return JsonResponse({"error": "La pregunta está vacía."}, status=400)
        doc = Document.objects.filter(chat_id=chat_id).first()
        if not doc or doc.status != "processed":
            return JsonResponse({"error": "La documentación no está procesada aún."}, status=400)
        chunks = Chunk.objects.filter(document=doc)
        context = " ".join([c.text[:400] for c in chunks[:5]])  # limit for demo

        # DEMO answer (replace with RAG+LLM later)
        answer = f"(Demo) Basado en la documentación, tu pregunta fue: '{question}'.\n\nContexto usado: {context[:300]}..."

        ChatHistory.objects.create(document=doc, question=question, answer=answer)
        return JsonResponse({"question": question, "answer": answer})
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

def chat_history(request, chat_id):
    doc = Document.objects.filter(chat_id=chat_id).first()
    if not doc:
        return JsonResponse({"history": []})
    history = ChatHistory.objects.filter(document=doc).order_by("created_at")
    data = [{"question": h.question, "answer": h.answer, "timestamp": h.created_at} for h in history]
    return JsonResponse({"history": data})

def prueba_de_formulario(request):
    return render(request, "form.html")