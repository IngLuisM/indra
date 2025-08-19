from django.db import models
import uuid

class Document(models.Model):
    """Representa un documento procesado"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_id = models.CharField(max_length=100, unique=True)  # ID de sesión
    url = models.URLField()
    status = models.CharField(
        max_length=50,
        default="processing",
        choices=[
            ("processing", "Processing"),
            ("processed", "Processed"),
            ("failed", "Failed"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc {self.chat_id} ({self.status})"


class Chunk(models.Model):
    """Fragmentos del documento vectorizados para RAG"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, related_name="chunks", on_delete=models.CASCADE)
    text = models.TextField()
    embedding = models.BinaryField(null=True, blank=True)  # Guardamos vector como binario opcional

    def __str__(self):
        return f"Chunk {str(self.id)[:8]} - Doc {self.document.chat_id}"


class ChatHistory(models.Model):
    """Historial de preguntas y respuestas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, related_name="history", on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:30]}... | Doc {self.document.chat_id}"
