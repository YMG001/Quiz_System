from typing import List, Dict
from app.models.qa_pair import QAPair
from app.database.db import db

class QuizService:
    @staticmethod
    def get_user_questions(user_id: int, count: int = None) -> List[Dict]:
        query = QAPair.query.filter_by(user_id=user_id).order_by(QAPair.id.desc())
        
        if count is not None:
            query = query.limit(count)
        
        questions = query.all()
        return [q.to_dict() for q in questions]
    
    @staticmethod
    def check_answer(question_id: int, user_id: int, user_answer: str) -> Dict:
        qa_pair = QAPair.query.filter_by(id=question_id, user_id=user_id).first()
        if not qa_pair:
            return {"correct": False, "message": "题目不存在或无权访问"}
            
        is_correct = user_answer.strip().lower() == qa_pair.answer.strip().lower()
        return {
            "correct": is_correct,
            "correct_answer": qa_pair.answer if not is_correct else None
        } 