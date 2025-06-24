Hybrid Processing Features:

Logical Table Detection: Automatically identifies separate tables within sheets
Structure Preservation: Maintains column relationships and table hierarchy
Contextual Headers: Adds descriptive context for each table chunk
Markdown Conversion: Converts tables to structured markdown format
Smart Chunking: Splits tables by logical boundaries rather than character limits

Metadata Enrichment Features:

Multi-Level Metadata: File, sheet, table, and chunk-level metadata
Column Analysis: Automatic detection of numeric vs text columns
Statistical Summaries: Mean, median, min, max for numeric columns
Data Quality Metrics: Data density, unique value counts
Structural Information: Row/column counts, data types, sample values

Key Benefits:

Preserves Table Context: Each chunk includes table headers and structure
Rich Retrieval Metadata: Enhanced filtering and ranking in vector search
Logical Chunking: Respects table boundaries instead of arbitrary splits
Comprehensive Analytics: Statistical insights for better understanding
Export Ready: JSON output format for vector database ingestion

Code:
```python
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

@dataclass
class TableChunk:
    """Represents a processed table chunk with metadata"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    table_id: str

class ExcelRAGProcessor:
    """
    Advanced Excel processor for RAG applications combining:
    1. Hybrid Processing (structured + contextual text)
    2. Metadata Enrichment
    """
    
    def __init__(self, 
                 max_rows_per_chunk: int = 50,
                 include_statistical_summary: bool = True,
                 preserve_formulas: bool = True):
        self.max_rows_per_chunk = max_rows_per_chunk
        self.include_statistical_summary = include_statistical_summary
        self.preserve_formulas = preserve_formulas
    
    def process_excel_file(self, file_path: str) -> List[TableChunk]:
        """
        Main method to process Excel file into RAG-ready chunks
        """
        file_path = Path(file_path)
        chunks = []
        
        # Read all sheets
        try:
            excel_data = pd.read_excel(file_path, sheet_name=None, dtype=str)
        except Exception as e:
            raise Exception(f"Error reading Excel file: {e}")
        
        # Process each sheet
        for sheet_name, df in excel_data.items():
            sheet_chunks = self._process_sheet(df, sheet_name, file_path)
            chunks.extend(sheet_chunks)
        
        return chunks
    
    def _process_sheet(self, df: pd.DataFrame, sheet_name: str, file_path: Path) -> List[TableChunk]:
        """Process a single sheet into chunks"""
        chunks = []
        
        # Clean the dataframe
        df_cleaned = self._clean_dataframe(df)
        
        # Generate sheet-level metadata
        sheet_metadata = self._generate_sheet_metadata(df_cleaned, sheet_name, file_path)
        
        # Detect logical tables within the sheet
        logical_tables = self._detect_logical_tables(df_cleaned)
        
        # Process each logical table
        for table_idx, (start_row, end_row, table_df) in enumerate(logical_tables):
            table_chunks = self._process_logical_table(
                table_df, sheet_name, table_idx, start_row, end_row, sheet_metadata
            )
            chunks.extend(table_chunks)
        
        return chunks
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Fill NaN values with empty string for processing
        df = df.fillna('')
        
        return df
    
    def _detect_logical_tables(self, df: pd.DataFrame) -> List[Tuple[int, int, pd.DataFrame]]:
        """
        Detect logical tables within a sheet based on empty rows/structure
        Returns list of (start_row, end_row, table_dataframe)
        """
        if df.empty:
            return []
        
        # Simple heuristic: split on rows that are mostly empty
        logical_tables = []
        current_start = 0
        
        for i in range(len(df)):
            row = df.iloc[i]
            non_empty_cells = sum(1 for cell in row if str(cell).strip())
            
            # If row has very few non-empty cells, it might be a separator
            if non_empty_cells <= 1 and i > current_start:
                if i - current_start > 1:  # Only create table if it has multiple rows
                    table_df = df.iloc[current_start:i].copy()
                    logical_tables.append((current_start, i-1, table_df))
                current_start = i + 1
        
        # Add the last table
        if current_start < len(df):
            table_df = df.iloc[current_start:].copy()
            logical_tables.append((current_start, len(df)-1, table_df))
        
        # If no logical separation found, treat entire sheet as one table
        if not logical_tables:
            logical_tables.append((0, len(df)-1, df.copy()))
        
        return logical_tables
    
    def _process_logical_table(self, table_df: pd.DataFrame, sheet_name: str, 
                              table_idx: int, start_row: int, end_row: int,
                              sheet_metadata: Dict) -> List[TableChunk]:
        """Process a logical table into chunks"""
        chunks = []
        
        # Generate table-level metadata
        table_metadata = self._generate_table_metadata(
            table_df, sheet_name, table_idx, start_row, end_row, sheet_metadata
        )
        
        # Create table header context
        header_context = self._create_header_context(table_df, sheet_name, table_idx)
        
        # Split table into manageable chunks
        table_chunks_data = self._chunk_table(table_df, header_context)
        
        # Create TableChunk objects
        for chunk_idx, chunk_data in enumerate(table_chunks_data):
            chunk_metadata = {**table_metadata}
            chunk_metadata.update({
                'chunk_index': chunk_idx,
                'chunk_row_start': chunk_data['row_start'],
                'chunk_row_end': chunk_data['row_end'],
                'chunk_row_count': chunk_data['row_count']
            })
            
            chunk_id = self._generate_chunk_id(sheet_name, table_idx, chunk_idx)
            table_id = f"{sheet_name}_table_{table_idx}"
            
            chunk = TableChunk(
                content=chunk_data['content'],
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                table_id=table_id
            )
            chunks.append(chunk)
        
        return chunks
    
    def _generate_sheet_metadata(self, df: pd.DataFrame, sheet_name: str, file_path: Path) -> Dict:
        """Generate comprehensive sheet-level metadata"""
        metadata = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'sheet_name': sheet_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'file_size_bytes': file_path.stat().st_size if file_path.exists() else 0,
            'processing_timestamp': pd.Timestamp.now().isoformat()
        }
        
        return metadata
    
    def _generate_table_metadata(self, table_df: pd.DataFrame, sheet_name: str,
                                table_idx: int, start_row: int, end_row: int,
                                sheet_metadata: Dict) -> Dict:
        """Generate comprehensive table-level metadata"""
        
        # Basic table info
        metadata = {
            **sheet_metadata,
            'table_index': table_idx,
            'table_start_row': start_row,
            'table_end_row': end_row,
            'table_row_count': len(table_df),
            'table_column_count': len(table_df.columns),
            'table_headers': list(table_df.columns),
        }
        
        # Column analysis
        column_info = {}
        numeric_columns = []
        text_columns = []
        
        for col in table_df.columns:
            col_data = table_df[col].dropna()
            if col_data.empty:
                continue
                
            # Try to identify column types
            numeric_count = sum(1 for x in col_data if self._is_numeric(str(x)))
            total_count = len(col_data)
            
            col_info = {
                'non_null_count': total_count,
                'numeric_ratio': numeric_count / total_count if total_count > 0 else 0,
                'unique_values': len(col_data.unique()),
                'sample_values': list(col_data.head(3).astype(str))
            }
            
            if numeric_count / total_count > 0.7:  # 70% numeric threshold
                numeric_columns.append(col)
                # Add statistical info for numeric columns
                if self.include_statistical_summary:
                    numeric_values = pd.to_numeric(col_data, errors='coerce').dropna()
                    if not numeric_values.empty:
                        col_info.update({
                            'mean': float(numeric_values.mean()),
                            'median': float(numeric_values.median()),
                            'std': float(numeric_values.std()),
                            'min': float(numeric_values.min()),
                            'max': float(numeric_values.max())
                        })
            else:
                text_columns.append(col)
            
            column_info[col] = col_info
        
        metadata.update({
            'column_info': column_info,
            'numeric_columns': numeric_columns,
            'text_columns': text_columns,
            'data_density': self._calculate_data_density(table_df)
        })
        
        return metadata
    
    def _create_header_context(self, table_df: pd.DataFrame, sheet_name: str, table_idx: int) -> str:
        """Create contextual header information"""
        context_parts = [
            f"## Table from Sheet: {sheet_name}",
            f"Table {table_idx + 1} of sheet",
            f"Columns: {', '.join(table_df.columns)}",
            f"Data rows: {len(table_df)}",
            ""
        ]
        
        # Add column descriptions if available
        if len(table_df.columns) > 0:
            context_parts.append("### Column Information:")
            for col in table_df.columns:
                sample_values = table_df[col].dropna().head(2).astype(str).tolist()
                if sample_values:
                    context_parts.append(f"- **{col}**: {', '.join(sample_values)}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _chunk_table(self, table_df: pd.DataFrame, header_context: str) -> List[Dict]:
        """Split table into chunks while preserving structure"""
        chunks = []
        
        if table_df.empty:
            return chunks
        
        # Always include headers in each chunk
        headers = list(table_df.columns)
        
        # Split into chunks based on row limit
        for start_idx in range(0, len(table_df), self.max_rows_per_chunk):
            end_idx = min(start_idx + self.max_rows_per_chunk, len(table_df))
            chunk_df = table_df.iloc[start_idx:end_idx]
            
            # Create markdown table
            markdown_table = self._dataframe_to_markdown(chunk_df)
            
            # Combine header context with table data
            content = f"{header_context}\n### Table Data:\n{markdown_table}"
            
            # Add row context
            content += f"\n\n*Showing rows {start_idx + 1} to {end_idx} of {len(table_df)} total rows*"
            
            chunks.append({
                'content': content,
                'row_start': start_idx,
                'row_end': end_idx - 1,
                'row_count': len(chunk_df)
            })
        
        return chunks
    
    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        """Convert dataframe to markdown table format"""
        if df.empty:
            return "*Empty table*"
        
        # Use pandas to_markdown if available, otherwise create manually
        try:
            return df.to_markdown(index=False, tablefmt='pipe')
        except AttributeError:
            # Fallback manual markdown creation
            lines = []
            headers = list(df.columns)
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            
            for _, row in df.iterrows():
                row_values = [str(val) if pd.notna(val) else "" for val in row]
                lines.append("| " + " | ".join(row_values) + " |")
            
            return "\n".join(lines)
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string value represents a number"""
        try:
            float(value.replace(',', '').replace('$', '').replace('%', ''))
            return True
        except (ValueError, AttributeError):
            return False
    
    def _calculate_data_density(self, df: pd.DataFrame) -> float:
        """Calculate the density of non-empty data in the table"""
        if df.empty:
            return 0.0
        
        total_cells = df.shape[0] * df.shape[1]
        non_empty_cells = df.count().sum()
        return non_empty_cells / total_cells if total_cells > 0 else 0.0
    
    def _generate_chunk_id(self, sheet_name: str, table_idx: int, chunk_idx: int) -> str:
        """Generate unique chunk ID"""
        content = f"{sheet_name}_{table_idx}_{chunk_idx}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def export_chunks_to_json(self, chunks: List[TableChunk], output_path: str):
        """Export processed chunks to JSON for further processing"""
        export_data = []
        for chunk in chunks:
            export_data.append({
                'chunk_id': chunk.chunk_id,
                'table_id': chunk.table_id,
                'content': chunk.content,
                'metadata': chunk.metadata
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = ExcelRAGProcessor(
        max_rows_per_chunk=30,
        include_statistical_summary=True,
        preserve_formulas=True
    )
    
    # Process Excel file
    try:
        chunks = processor.process_excel_file("sample_data.xlsx")
        
        # Display results
        print(f"Processed {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
            print(f"\n--- Chunk {i+1} ---")
            print(f"ID: {chunk.chunk_id}")
            print(f"Table ID: {chunk.table_id}")
            print("\nContent Preview:")
            print(chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content)
            print(f"\nMetadata Keys: {list(chunk.metadata.keys())}")
            print(f"Sheet: {chunk.metadata.get('sheet_name')}")
            print(f"Columns: {chunk.metadata.get('table_headers')}")
            print(f"Rows: {chunk.metadata.get('chunk_row_count')}")
        
        # Export to JSON for vector database ingestion
        processor.export_chunks_to_json(chunks, "processed_excel_chunks.json")
        print(f"\nExported chunks to processed_excel_chunks.json")
        
    except Exception as e:
        print(f"Error processing file: {e}")
```
Usage Example:

```python
# Initialize with custom settings
processor = ExcelRAGProcessor(
    max_rows_per_chunk=50,  # Adjust based on your needs
    include_statistical_summary=True,
    preserve_formulas=True
)

# Process your Excel file
chunks = processor.process_excel_file("your_data.xlsx")

# Each chunk now contains structured content + rich metadata
for chunk in chunks:
    # Use chunk.content for vector embedding
    # Use chunk.metadata for filtering and ranking
    vector_db.add_document(chunk.content, metadata=chunk.metadata)
```

This approach ensures your RAG system can effectively retrieve table-based information while maintaining the structural relationships that make Excel data meaningful.