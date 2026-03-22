"""
文档处理模块
提供文档切割、清洗和预处理功能
"""
from typing import List, Optional
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import re

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器"""
    
    DEFAULT_SEPARATORS = [
        "\n\n",
        "\n",
        "。",
        "！",
        "？",
        "；",
        "，",
        " ",
        ""
    ]
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False
        )
        
        logger.info(
            f"DocumentProcessor initialized: "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
    
    def split_documents(
        self,
        documents: List[Document],
        add_metadata: bool = True
    ) -> List[Document]:
        """切割文档"""
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            chunks = self.text_splitter.split_documents([doc])
            
            if add_metadata:
                for chunk_idx, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        "chunk_index": chunk_idx,
                        "chunk_total": len(chunks),
                        "doc_index": doc_idx,
                        "original_length": len(doc.page_content),
                        "chunk_length": len(chunk.page_content)
                    })
            
            all_chunks.extend(chunks)
            logger.info(
                f"Split document {doc_idx}: "
                f"{len(doc.page_content)} chars -> {len(chunks)} chunks"
            )
        
        logger.info(f"Total: {len(documents)} docs -> {len(all_chunks)} chunks")
        return all_chunks
    
    def split_text(
        self,
        text: str,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """切割文本"""
        doc = Document(page_content=text, metadata=metadata or {})
        return self.split_documents([doc])
    
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.replace('\t', ' ')
        text = text.strip()
        return text
    
    def process_documents(
        self,
        documents: List[Document],
        clean: bool = True,
        split: bool = True
    ) -> List[Document]:
        """处理文档（清洗 + 切割）"""
        processed_docs = []
        
        for doc in documents:
            if clean:
                content = self.clean_text(doc.page_content)
                doc = Document(page_content=content, metadata=doc.metadata)
            
            processed_docs.append(doc)
        
        if split:
            processed_docs = self.split_documents(processed_docs)
        
        return processed_docs
