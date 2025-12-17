"""
Content ingestion pipeline service
Handles reading Docusaurus book content, normalizing and chunking for semantic retrieval
"""
import os
import re
from typing import List, Dict, Any
from pathlib import Path
from ..models.content import BookContent, ContentChunk
import logging

logger = logging.getLogger(__name__)

class IngestionService:
    """Service for ingesting Docusaurus book content"""

    def __init__(self):
        self.supported_extensions = ['.md', '.mdx']
        logger.info("Ingestion service initialized")

    def read_docusaurus_content(self, docs_path: str) -> List[Dict[str, str]]:
        """Read content from Docusaurus docs directory"""
        content_list = []

        if not os.path.exists(docs_path):
            logger.warning(f"Docs path does not exist: {docs_path}")
            return content_list

        for root, dirs, files in os.walk(docs_path):
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, docs_path)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            content_list.append({
                                'title': self._extract_title(content, file),
                                'content': content,
                                'source_path': f"/docs/{relative_path}",
                                'section': self._extract_section_from_path(relative_path)
                            })
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {str(e)}")
                        continue

        logger.info(f"Read {len(content_list)} content files from {docs_path}")
        return content_list

    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from content or use filename as fallback"""
        # Try to extract title from markdown heading
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().startswith('# '):
                return line.strip()[2:]  # Remove '# ' prefix

        # Fallback to filename
        return os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()

    def _extract_section_from_path(self, path: str) -> str:
        """Extract section name from file path"""
        # Get the directory structure as the section
        directory = os.path.dirname(path)
        if directory:
            return directory.replace(os.sep, ' - ')
        return "Introduction"

    def chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Chunk content into smaller pieces for embedding"""
        chunks = []

        # Split content into sentences to avoid breaking sentences
        sentences = re.split(r'(?<=[.!?]) +', content)

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk + " " + sentence) <= chunk_size:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Handle sentences longer than chunk_size by splitting them
                if len(sentence) > chunk_size:
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk + " " + word) <= chunk_size:
                            if temp_chunk:
                                temp_chunk += " " + word
                            else:
                                temp_chunk = word
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                temp_chunk = word
                    if temp_chunk:
                        chunks.append(temp_chunk.strip())
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Apply overlap between chunks
        if overlap > 0 and len(chunks) > 1:
            overlapping_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # Get the last 'overlap' characters from the previous chunk
                    prev_chunk_end = chunks[i-1][-overlap:]
                    chunk_with_overlap = prev_chunk_end + " " + chunk
                    overlapping_chunks.append(chunk_with_overlap.strip())
                else:
                    overlapping_chunks.append(chunk)
            return overlapping_chunks

        return chunks

    def prepare_content_for_embedding(self, raw_content: List[Dict[str, str]]) -> List[BookContent]:
        """Prepare content for embedding by chunking and creating BookContent objects"""
        book_contents = []

        for idx, item in enumerate(raw_content):
            content_chunks = self.chunk_content(item['content'])

            # Create a BookContent object for each chunk
            for chunk_idx, chunk_text in enumerate(content_chunks):
                content_id = f"{item['source_path']}_chunk_{chunk_idx}"

                book_content = BookContent(
                    id=content_id,
                    title=f"{item['title']} - Part {chunk_idx + 1}",
                    content=chunk_text,
                    source_path=item['source_path'],
                    section=item['section'],
                    metadata={
                        'original_title': item['title'],
                        'chunk_index': chunk_idx,
                        'total_chunks': len(content_chunks)
                    }
                )
                book_contents.append(book_content)

        logger.info(f"Prepared {len(book_contents)} content chunks for embedding")
        return book_contents

    def process_docusaurus_docs(self, docs_path: str) -> List[BookContent]:
        """Complete process: read, chunk, and prepare Docusaurus docs for embedding"""
        logger.info(f"Starting ingestion process for docs at: {docs_path}")

        # Read raw content
        raw_content = self.read_docusaurus_content(docs_path)

        if not raw_content:
            logger.warning("No content found to process")
            return []

        # Prepare content for embedding
        book_contents = self.prepare_content_for_embedding(raw_content)

        logger.info(f"Ingestion process completed. Prepared {len(book_contents)} content items for embedding")
        return book_contents

# Global instance
ingestion_service = IngestionService()