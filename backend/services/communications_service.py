# backend/services/communications_service.py
import json
from typing import Dict
import google.generativeai as genai
from config import Config
from models import CustomerMessage, ValidationResult


class CommunicationsService:
    """Communications Agent: Generates professional customer responses from validation results."""
    
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def generate_customer_message(self, validation_result: ValidationResult) -> CustomerMessage:
        """Generate a professional customer message from a ValidationResult."""
        try:
            prompt = self._create_communications_prompt(validation_result)
            response = self.model.generate_content(prompt)
            subject, body = self._extract_subject_and_body(response.text)
            status = validation_result.overall_status
            return CustomerMessage(subject=subject, body=body, status=status)
        except Exception as e:
            return CustomerMessage(subject="Error", body=f"Failed to generate message: {str(e)}", status="error")
    
    def _create_communications_prompt(self, validation_result: ValidationResult) -> str:
        """Create a prompt for the Communications Agent based on ValidationResult."""
        return f"""
        You are Alex, a senior customer service representative. Write a professional email to a customer based on an order processing summary.

        PERSONA: Professional, polite, helpful, empathetic

        EMAIL RULES:

        If customer status is "unknown_customer":
        - Acknowledge their interest in our products
        - Explain they need to register first
        - Provide registration instructions
        - Offer assistance
        - Include contact information

        If overall status is "success":
        - Write confirmation email
        - Thank customer by name
        - List successful items
        - Mention shipping notification
        - End positively

        If overall status is "partial_success" or "failure":
        - Thank for order
        - State need for input on some items
        - Create "Items Requiring Attention" section
        - Explain each error clearly (include specific error messages for each failed product)
        - If suggestions exist, create "Suggested Alternatives" section
        - List successful items if any
        - Ask for changes or confirmation
        - Apologize for inconvenience

        If products not found:
        - Explain clearly
        - Suggest checking current catalog
        - Offer help finding similar products
        - Provide contact information

        FORMAT: Proper email with subject line, clear sections, good spacing

        BRIEFING DOCUMENT: {json.dumps(validation_result.dict(), indent=2)}

        Generate a complete, professional email response. Output the subject line on the first line, then a blank line, then the email body.
        """
    
    def _extract_subject_and_body(self, response_text: str):
        """Extract subject and body from LLM response."""
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split('\n')
            if len(lines) > 1:
                cleaned = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])
        cleaned = cleaned.replace('```', '').strip()
        lines = cleaned.split('\n', 1)
        if len(lines) == 2:
            subject = lines[0].strip()
            body = lines[1].strip()
        else:
            subject = "Customer Order Update"
            body = cleaned
        return subject, body 