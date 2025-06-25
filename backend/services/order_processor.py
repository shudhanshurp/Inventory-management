from services.info_extractor_service import InfoExtractorService
from services.validator_service import ValidatorService
from services.communications_service import CommunicationsService
from services.db_update_service import DBUpdateService
from models import ExtractedOrderInfo, ValidationResult, CustomerMessage, OrderUpdateResult

class OrderProcessor:
    @staticmethod
    def process_order(email_text: str) -> dict:
        result = {}
        try:
            extracted_info = InfoExtractorService.extract_info(email_text)
            result['extracted_info'] = extracted_info.dict()
        except Exception as e:
            result['extracted_info'] = {'error': str(e)}
            return result
        try:
            validation_result = ValidatorService.validate_order(extracted_info)
            result['validation_result'] = validation_result.dict()
        except Exception as e:
            result['validation_result'] = {'error': str(e)}
            return result
        try:
            customer_message = CommunicationsService().generate_customer_message(validation_result)
            result['customer_message'] = customer_message.dict()
        except Exception as e:
            result['customer_message'] = {'error': str(e)}
        try:
            order_update_result = DBUpdateService.update_order(validation_result)
            result['order_update_result'] = order_update_result.dict()
        except Exception as e:
            result['order_update_result'] = {'error': str(e)}
        return result 