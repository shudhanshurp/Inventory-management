from services.info_extractor_service import InfoExtractorService
from services.validator_service import ValidatorService
from services.communications_service import CommunicationsService
from services.db_update_service import DBUpdateService
from models import ExtractedOrderInfo, ValidationResult, CustomerMessage, OrderUpdateResult

class OrderProcessor:
    def __init__(self,
                 info_extractor_service_instance: InfoExtractorService,
                 validator_service_instance: ValidatorService,
                 communications_service_instance: CommunicationsService,
                 db_update_service_instance: DBUpdateService):
        self.info_extractor_service = info_extractor_service_instance
        self.validator_service = validator_service_instance
        self.communications_service = communications_service_instance
        self.db_update_service = db_update_service_instance

    def process_order(self, email_text: str) -> dict:
        # print(f"[OrderProcessor] Starting process_order for email: {email_text[:100]}...")
        result = {}
        try:
            extracted_info = self.info_extractor_service.extract_info(email_text)
            # print(f"[OrderProcessor] Extracted info: {extracted_info.json()}")
            result['extracted_info'] = extracted_info.dict()
        except Exception as e:
            print(f"[OrderProcessor] Error in process_order: {e}")
            result['extracted_info'] = {'error': str(e)}
            return result
        try:
            validation_result = self.validator_service.validate_order(extracted_info)
            # print(f"[OrderProcessor] Validation result: {validation_result.json()}")
            result['validation_result'] = validation_result.dict()
        except Exception as e:
            print(f"[OrderProcessor] Error in process_order: {e}")
            result['validation_result'] = {'error': str(e)}
            return result
        try:
            customer_message = self.communications_service.generate_customer_message(validation_result)
            # print(f"[OrderProcessor] Customer message status: {customer_message.status}")
            result['customer_message'] = customer_message.dict()
        except Exception as e:
            print(f"[OrderProcessor] Error in process_order: {e}")
            result['customer_message'] = {'error': str(e)}
        try:
            # print("[OrderProcessor] About to call DBUpdateService.update_order...")
            order_update_result = self.db_update_service.update_order(validation_result)
            # print(f"[OrderProcessor] DB update result: {order_update_result.success}, ID: {order_update_result.order_id}")
            result['order_update_result'] = order_update_result.dict()
        except Exception as e:
            print(f"[OrderProcessor] Error in process_order: {e}")
            result['order_update_result'] = {'error': str(e)}
        # print(f"[OrderProcessor] Finished process_order for: {validation_result.customer_info.get('id')}, Status: {validation_result.overall_status}")
        return result 