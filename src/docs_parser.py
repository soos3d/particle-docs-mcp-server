"""Documentation parser for structuring content."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ContentSection:
    """Represents a section of documentation content."""
    title: str
    content: str
    level: int
    anchor: Optional[str] = None


@dataclass
class CodeBlock:
    """Represents a code block in documentation."""
    language: Optional[str]
    content: str
    line_number: int


@dataclass
class ParsedContent:
    """Structured representation of parsed documentation."""
    title: str
    sections: List[ContentSection]
    code_blocks: List[CodeBlock]
    links: List[Dict[str, str]]
    summary: str


class DocsParser:
    """Parses and structures documentation content."""
    
    def __init__(self):
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    def _extract_sections(self, content: str) -> List[ContentSection]:
        """Extract sections based on markdown headers."""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            header_match = self.header_pattern.match(line)
            
            if header_match:
                # Save previous section if exists
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                anchor = self._generate_anchor(title)
                
                current_section = ContentSection(
                    title=title,
                    content="",
                    level=level,
                    anchor=anchor
                )
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add final section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        return sections
    
    def _generate_anchor(self, title: str) -> str:
        """Generate URL anchor from section title."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def _extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """Extract code blocks from content."""
        code_blocks = []
        lines = content.split('\n')
        
        for match in self.code_block_pattern.finditer(content):
            language = match.group(1)
            code_content = match.group(2)
            
            # Find line number where this code block starts
            line_number = content[:match.start()].count('\n') + 1
            
            code_blocks.append(CodeBlock(
                language=language,
                content=code_content,
                line_number=line_number
            ))
        
        return code_blocks
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from content."""
        links = []
        
        for match in self.link_pattern.finditer(content):
            text = match.group(1)
            url = match.group(2)
            
            links.append({
                "text": text,
                "url": url,
                "is_external": not url.startswith('#') and not url.startswith('/')
            })
        
        return links
    
    def _generate_summary(self, content: str, max_length: int = 300) -> str:
        """Generate a summary of the content."""
        # Remove code blocks and links for summary
        clean_content = self.code_block_pattern.sub('', content)
        clean_content = self.link_pattern.sub(r'\1', clean_content)
        
        # Remove headers and extra whitespace
        clean_content = self.header_pattern.sub('', clean_content)
        clean_content = re.sub(r'\n+', ' ', clean_content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Truncate to max length
        if len(clean_content) > max_length:
            clean_content = clean_content[:max_length].rsplit(' ', 1)[0] + '...'
        
        return clean_content
    
    def parse_content(self, content: str, title: str = "") -> ParsedContent:
        """Parse raw content into structured format."""
        sections = self._extract_sections(content)
        code_blocks = self._extract_code_blocks(content)
        links = self._extract_links(content)
        summary = self._generate_summary(content)
        
        # Extract title from first section if not provided
        if not title and sections:
            title = sections[0].title
        
        return ParsedContent(
            title=title,
            sections=sections,
            code_blocks=code_blocks,
            links=links,
            summary=summary
        )
    
    def get_section_by_anchor(self, parsed_content: ParsedContent, anchor: str) -> Optional[ContentSection]:
        """Get a specific section by its anchor."""
        for section in parsed_content.sections:
            if section.anchor == anchor:
                return section
        return None
    
    def search_content(self, parsed_content: ParsedContent, query: str) -> List[ContentSection]:
        """Search for sections containing the query."""
        query_lower = query.lower()
        matching_sections = []
        
        for section in parsed_content.sections:
            if (query_lower in section.title.lower() or 
                query_lower in section.content.lower()):
                matching_sections.append(section)
        
        return matching_sections
