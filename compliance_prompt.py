import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains import LLMChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document

# Define Pydantic models for structured output
class HistoricalQuestion(BaseModel):
    question: str = Field(description="Similar historical question")
    outcome: str = Field(description="Previous compliance status")
    relevance: str = Field(description="How this relates to current question")

class DocumentationEvidence(BaseModel):
    source: str = Field(description="Documentation section/page reference")
    content: str = Field(description="Key excerpt or capability description")
    relevance: str = Field(description="How this supports the conclusion")

class ComplianceReasoning(BaseModel):
    requirement_interpretation: str = Field(description="How you interpreted the core requirement")
    historical_influence: str = Field(description="How historical questions influenced your decision")
    documentation_evidence: str = Field(description="Evidence from product documentation")
    assumptions_limitations: str = Field(description="Any assumptions or limitations in assessment")

class SupportingEvidence(BaseModel):
    historical_questions: List[HistoricalQuestion]
    product_documentation: List[DocumentationEvidence]

class ComplianceMetadata(BaseModel):
    assessment_timestamp: str = Field(description="ISO timestamp of assessment")
    primary_requirements: List[str] = Field(description="List of core requirements identified")
    evidence_quality: str = Field(description="Overall quality of available evidence")

class ComplianceAssessment(BaseModel):
    compliance_status: str = Field(description="Compliance status")
    confidence_level: str = Field(description="Confidence level")
    key_findings: List[str] = Field(description="Key findings supporting the decision")
    reasoning: ComplianceReasoning
    supporting_evidence: SupportingEvidence
    risk_factors: List[str] = Field(description="Risk factors affecting compliance")
    recommendations: List[str] = Field(description="Recommendations for improvement")
    metadata: ComplianceMetadata

# Compliance Assessment Chain
class ComplianceAssessmentChain:
    def __init__(self, model_name: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434"):
        self.llm = OllamaLLM(
            model=model_name,
            base_url=base_url,
            temperature=0.1,  # Low temperature for consistent outputs
            num_predict=2048,  # Adequate tokens for JSON response
        )
        
        # Set up JSON output parser
        self.parser = JsonOutputParser(pydantic_object=ComplianceAssessment)
        
        # Define the prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["current_question", "historical_questions", "product_documentation"],
            template=self._get_prompt_template(),
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        # Create the chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            output_parser=self.parser
        )
    
    def _get_prompt_template(self) -> str:
        return """# RFQ Compliance Assessment

You are an expert compliance analyst tasked with determining whether our product meets the requirements specified in RFQ questions. You will be provided with:

1. **Current Question**: The RFQ question that needs to be assessed
2. **Similar Historical Questions**: Previously answered RFQ questions from our database with their compliance status
3. **Product Documentation**: Relevant excerpts from our product documentation retrieved via vector search

## Your Task

Analyze the provided information and determine the compliance status for the current question. You must categorize the compliance as one of these four states:

- **Fully Compliant**: Our product completely meets all requirements specified in the question
- **Partially Compliant**: Our product meets some but not all requirements, or meets requirements with limitations
- **Not Compliant**: Our product does not meet the specified requirements
- **Unknown**: Insufficient information available to make a determination

## Analysis Framework

### Step 1: Question Understanding
- Extract the core requirement(s) from the current question
- Identify any specific technical specifications, standards, or capabilities mentioned
- Note any compliance thresholds, timelines, or quantitative requirements

### Step 2: Historical Context Analysis
- Review similar questions and their previous compliance assessments
- Identify patterns in how similar requirements were evaluated
- Note any discrepancies or evolving interpretations
- Consider the relevance and recency of historical assessments

### Step 3: Product Capability Assessment
- Analyze the product documentation for evidence supporting or contradicting compliance
- Look for explicit mentions of required features, standards, or capabilities
- Identify any limitations, exceptions, or conditional compliance scenarios
- Consider implementation status (current vs. planned features)

### Step 4: Evidence Synthesis
- Weigh the strength and quality of evidence from both sources
- Resolve any conflicts between historical assessments and current documentation
- Account for product updates or changes since historical assessments

## Guidelines

1. **Prioritize Recent and Relevant Information**: Give more weight to recent product documentation and similar historical questions
2. **Be Conservative**: When in doubt, err on the side of lower compliance rather than overstating capabilities
3. **Distinguish Between Current and Future Capabilities**: Clearly indicate if compliance depends on planned features
4. **Consider Context**: RFQ requirements may have different interpretations in different contexts
5. **Document Assumptions**: Explicitly state any assumptions you're making in your assessment
6. **Flag Uncertainties**: Don't hesitate to use "Unknown" when evidence is insufficient or contradictory

**Current Question**: {current_question}

**Similar Historical Questions**:
{historical_questions}

**Product Documentation**:
{product_documentation}

{format_instructions}

**IMPORTANT**: Return ONLY the JSON object. Do not include any additional text, explanations, or markdown formatting outside the JSON structure."""

    def assess_compliance(
        self, 
        current_question: str, 
        historical_questions: str, 
        product_documentation: str
    ) -> Dict[str, Any]:
        """
        Assess compliance for a given RFQ question
        """
        try:
            result = self.chain.run(
                current_question=current_question,
                historical_questions=historical_questions,
                product_documentation=product_documentation
            )
            return result
        except Exception as e:
            # Fallback response in case of parsing errors
            return {
                "compliance_status": "Unknown",
                "confidence_level": "Low",
                "key_findings": [f"Error in assessment: {str(e)}"],
                "reasoning": {
                    "requirement_interpretation": "Unable to process due to error",
                    "historical_influence": "Not assessed",
                    "documentation_evidence": "Not assessed",
                    "assumptions_limitations": f"Processing error: {str(e)}"
                },
                "supporting_evidence": {
                    "historical_questions": [],
                    "product_documentation": []
                },
                "risk_factors": ["Assessment failed due to technical error"],
                "recommendations": ["Retry assessment or review input data"],
                "metadata": {
                    "assessment_timestamp": datetime.now().isoformat(),
                    "primary_requirements": [],
                    "evidence_quality": "Unknown"
                }
            }

# RAG Retrieval Components
class RAGComplianceSystem:
    def __init__(self, 
                 model_name: str = "deepseek-r1:8b",
                 embedding_model: str = "nomic-embed-text:latest"):
        
        # Initialize components
        self.compliance_chain = ComplianceAssessmentChain(model_name)
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        
        # Initialize vector stores (you would populate these with your data)
        self.historical_vectorstore = None  # Chroma vectorstore for historical questions
        self.product_vectorstore = None     # Chroma vectorstore for product docs
    
    def setup_vectorstores(self, 
                          historical_docs: List[Document], 
                          product_docs: List[Document]):
        """
        Setup vector stores with your documents
        """
        self.historical_vectorstore = Chroma.from_documents(
            documents=historical_docs,
            embedding=self.embeddings,
            collection_name="historical_questions"
        )
        
        self.product_vectorstore = Chroma.from_documents(
            documents=product_docs,
            embedding=self.embeddings,
            collection_name="product_documentation"
        )
    
    def retrieve_historical_questions(self, query: str, k: int = 5) -> str:
        """
        Retrieve similar historical questions using your multi-stage approach
        """
        if not self.historical_vectorstore:
            return "No historical questions available"
        
        # Step 1: Cosine similarity (vector search)
        similar_docs = self.historical_vectorstore.similarity_search(query, k=k)
        
        # TODO: Implement your additional matching stages:
        # Step 2: Cross-encoder re-ranking
        # Step 3: Fuzzy matching
        # Step 4: Exact match using lemmatization
        
        # Format results for the prompt
        formatted_results = []
        for i, doc in enumerate(similar_docs, 1):
            formatted_results.append(f"{i}. Question: {doc.page_content}")
            if doc.metadata:
                formatted_results.append(f"   Previous Status: {doc.metadata.get('compliance_status', 'Unknown')}")
                formatted_results.append(f"   Confidence: {doc.metadata.get('confidence', 'Unknown')}")
        
        return "\n".join(formatted_results)
    
    def retrieve_product_documentation(self, query: str, k: int = 5) -> str:
        """
        Retrieve relevant product documentation
        """
        if not self.product_vectorstore:
            return "No product documentation available"
        
        similar_docs = self.product_vectorstore.similarity_search(query, k=k)
        
        # Format results for the prompt
        formatted_results = []
        for i, doc in enumerate(similar_docs, 1):
            formatted_results.append(f"{i}. Source: {doc.metadata.get('source', 'Unknown')}")
            formatted_results.append(f"   Content: {doc.page_content}")
        
        return "\n".join(formatted_results)
    
    def assess_rfq_compliance(self, rfq_question: str) -> Dict[str, Any]:
        """
        Main method to assess RFQ compliance
        """
        # Retrieve similar historical questions
        historical_context = self.retrieve_historical_questions(rfq_question)
        
        # Retrieve relevant product documentation
        product_context = self.retrieve_product_documentation(rfq_question)
        
        # Assess compliance
        result = self.compliance_chain.assess_compliance(
            current_question=rfq_question,
            historical_questions=historical_context,
            product_documentation=product_context
        )
        
        return result

# Usage Example
def main():
    # Initialize the system
    compliance_system = RAGComplianceSystem(
        model_name="deepseek-r1:8b",  # or "qwen2.5:3b"
        embedding_model="nomic-embed-text:latest"
    )
    
    # Example historical questions (you would load these from your database)
    historical_docs = [
        Document(
            page_content="Does your product support SAML 2.0 authentication?",
            metadata={"compliance_status": "Fully Compliant", "confidence": "High"}
        ),
        Document(
            page_content="Can your system integrate with Active Directory?",
            metadata={"compliance_status": "Partially Compliant", "confidence": "Medium"}
        )
    ]
    
    # Example product documentation
    product_docs = [
        Document(
            page_content="Our authentication module supports SAML 2.0, OAuth 2.0, and LDAP integration.",
            metadata={"source": "Authentication Guide v2.1"}
        ),
        Document(
            page_content="Active Directory integration is available through our LDAP connector with some limitations on nested groups.",
            metadata={"source": "Integration Manual v1.5"}
        )
    ]
    
    # Setup vector stores
    compliance_system.setup_vectorstores(historical_docs, product_docs)
    
    # Assess a new RFQ question
    rfq_question = "Does your product support single sign-on with SAML authentication?"
    
    try:
        result = compliance_system.assess_rfq_compliance(rfq_question)
        print("Compliance Assessment Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error during assessment: {e}")

if __name__ == "__main__":
    main()