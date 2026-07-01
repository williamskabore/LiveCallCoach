import logging
import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
from watchfiles import watch

from backend.config import config
from backend.api.models import KnowledgeBaseEntry

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.kb_directory = Path(config.KB_DIRECTORY)
        self.entries: Dict[str, KnowledgeBaseEntry] = {}
        self.file_hashes: Dict[str, str] = {}
        self._load_knowledge_base()
        
        if config.KB_WATCH_ENABLED:
            self._start_file_watcher()
    
    def _load_knowledge_base(self):
        """Load all markdown files from KB directory"""
        if not self.kb_directory.exists():
            logger.warning(f"KB directory {self.kb_directory} does not exist")
            self.kb_directory.mkdir(parents=True, exist_ok=True)
            return
        
        for file_path in self.kb_directory.glob("*.md"):
            self._load_file(file_path)
        
        logger.info(f"Loaded {len(self.entries)} KB entries")
    
    def _load_file(self, file_path: Path):
        """Load a single markdown file into KB"""
        try:
            content = file_path.read_text(encoding='utf-8')
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Parse front matter if exists
            metadata = self._parse_front_matter(content)
            
            entry = KnowledgeBaseEntry(
                title=metadata.get('title', file_path.stem),
                content=metadata.get('body', content),
                category=metadata.get('category', 'general'),
                tags=metadata.get('tags', []),
                last_updated=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
            
            self.entries[file_path.stem] = entry
            self.file_hashes[str(file_path)] = file_hash
            
        except Exception as e:
            logger.error(f"Error loading KB file {file_path}: {str(e)}")
    
    def _parse_front_matter(self, content: str) -> dict:
        """Parse YAML front matter from markdown"""
        result = {'body': content}
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                    if metadata:
                        result.update(metadata)
                    result['body'] = parts[2].strip()
                except yaml.YAMLError as e:
                    logger.warning(f"Error parsing front matter: {e}")
        
        return result
    
    def _start_file_watcher(self):
        """Start watching KB directory for changes"""
        import threading
        
        def watch_directory():
            try:
                for changes in watch(self.kb_directory):
                    for change_type, file_path in changes:
                        path = Path(file_path)
                        if path.suffix == '.md':
                            if change_type == 'modified' or change_type == 'added':
                                self._load_file(path)
                                logger.info(f"KB file updated: {path.name}")
                            elif change_type == 'deleted':
                                key = path.stem
                                if key in self.entries:
                                    del self.entries[key]
                                logger.info(f"KB file removed: {path.name}")
            except Exception as e:
                logger.error(f"File watcher error: {e}")
        
        watcher_thread = threading.Thread(target=watch_directory, daemon=True)
        watcher_thread.start()
    
    def search(self, query: str, max_results: int = 5) -> List[KnowledgeBaseEntry]:
        """Search knowledge base entries"""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            score = self._calculate_relevance(entry, query_lower)
            if score > 0:
                results.append((score, entry))
        
        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [entry for _, entry in results[:max_results]]
    
    def _calculate_relevance(self, entry: KnowledgeBaseEntry, query: str) -> float:
        """Calculate relevance score for search"""
        score = 0.0
        
        # Check title
        if query in entry.title.lower():
            score += 10.0
        
        # Check content
        if query in entry.content.lower():
            score += 5.0
        
        # Check tags
        for tag in entry.tags:
            if query in tag.lower():
                score += 3.0
        
        # Check category
        if query in entry.category.lower():
            score += 2.0
        
        return score
    
    def get_entry(self, title: str) -> Optional[KnowledgeBaseEntry]:
        """Get specific KB entry by title"""
        return self.entries.get(title)
    
    def get_all_entries(self) -> List[KnowledgeBaseEntry]:
        """Get all KB entries"""
        return list(self.entries.values())
