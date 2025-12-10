"""ChromaDB vector store for semantic search of conversations and medical notes."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import config
from pathlib import Path


class VectorStore:
    """Manages vector embeddings for semantic search."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        # Ensure ChromaDB directory exists
        config.CHROMADB_PATH.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client (persistent)
        self.client = chromadb.PersistentClient(
            path=str(config.CHROMADB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collections
        self.conversations_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Patient conversation transcripts and summaries"}
        )
        
        self.medical_notes_collection = self.client.get_or_create_collection(
            name="medical_notes",
            metadata={"description": "Structured medical notes and visit summaries"}
        )
    
    def add_conversation(
        self,
        visit_id: int,
        patient_id: int,
        transcription: str,
        summary: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a conversation to the vector store.
        
        Args:
            visit_id: Visit ID
            patient_id: Patient ID
            transcription: Full transcription text
            summary: Visit summary
            metadata: Additional metadata
        """
        # Combine transcription and summary for better semantic understanding
        combined_text = f"{summary}\n\n{transcription[:1000]}"  # Limit transcription length
        
        # Prepare metadata
        doc_metadata = {
            "visit_id": visit_id,
            "patient_id": patient_id,
            "type": "conversation",
            **(metadata or {})
        }
        
        # Add to collection
        self.conversations_collection.add(
            documents=[combined_text],
            ids=[f"visit_{visit_id}"],
            metadatas=[doc_metadata]
        )
    
    def add_medical_note(
        self,
        note_id: str,
        patient_id: int,
        note_text: str,
        note_type: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a medical note to the vector store.
        
        Args:
            note_id: Unique note identifier
            patient_id: Patient ID
            note_text: Note content
            note_type: Type of note (diagnosis, recommendation, etc.)
            metadata: Additional metadata
        """
        doc_metadata = {
            "patient_id": patient_id,
            "note_type": note_type,
            "type": "medical_note",
            **(metadata or {})
        }
        
        self.medical_notes_collection.add(
            documents=[note_text],
            ids=[note_id],
            metadatas=[doc_metadata]
        )
    
    def search_conversations(
        self,
        query: str,
        patient_id: Optional[int] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search conversations semantically.
        
        Args:
            query: Search query
            patient_id: Optional filter by patient
            n_results: Number of results to return
        
        Returns:
            List of matching conversations with metadata
        """
        # Build query filter
        where = None
        if patient_id:
            where = {"patient_id": patient_id}
        
        results = self.conversations_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
        
        return formatted_results
    
    def search_medical_notes(
        self,
        query: str,
        patient_id: Optional[int] = None,
        note_type: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search medical notes semantically.
        
        Args:
            query: Search query
            patient_id: Optional filter by patient
            note_type: Optional filter by note type
            n_results: Number of results to return
        
        Returns:
            List of matching notes with metadata
        """
        # Build query filter
        where = {}
        if patient_id:
            where["patient_id"] = patient_id
        if note_type:
            where["note_type"] = note_type
        
        where = where if where else None
        
        results = self.medical_notes_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
        
        return formatted_results
    
    def search_all(
        self,
        query: str,
        patient_id: Optional[int] = None,
        n_results: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Search across all collections.
        
        Returns:
            Dictionary with 'conversations' and 'medical_notes' keys
        """
        return {
            "conversations": self.search_conversations(query, patient_id, n_results // 2),
            "medical_notes": self.search_medical_notes(query, patient_id, None, n_results // 2)
        }
    
    def delete_visit(self, visit_id: int):
        """Delete a visit from the vector store."""
        try:
            self.conversations_collection.delete(ids=[f"visit_{visit_id}"])
        except Exception as e:
            print(f"Error deleting visit from vector store: {e}")
    
    def get_patient_conversations(self, patient_id: int) -> List[Dict]:
        """Get all conversations for a patient."""
        results = self.conversations_collection.get(
            where={"patient_id": patient_id}
        )
        
        formatted_results = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                formatted_results.append({
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
        
        return formatted_results

