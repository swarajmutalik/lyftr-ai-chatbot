import json
from datetime import datetime,  timezone

from sqlalchemy.orm import Session
from models import Message

def get_session_messages(
    db: Session,
    session_id: str
):
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.id.asc())
        .all()
    )
    
def save_conversation(
    db:Session,
    session_id: str,
    user_message:str,
    assistant_reply:str,
    metadata: dict,
):
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()
    
    user_record = Message(
        session_id=session_id,
        role="user",
        content=user_message,
        metadata_json=None,
        created_at=timestamp
    )
    
    assistant_record = Message(
        session_id=session_id,
        role="assistant",
        content=assistant_reply,
        metadata_json=json.dumps(metadata),
        created_at=timestamp
    )
    
    try:
        db.add_all([
            user_record,
            assistant_record
        ])
        
        db.commit()
        
    except Exception:
        db.rollback()
        raise
    

def format_session_messages(messages):
    result = []

    for message in messages:
        item = {
            "role": message.role,
            "content": message.content
        }

        if message.role == "assistant":
            item["metadata"] = (
                json.loads(message.metadata_json)
                if message.metadata_json
                else {}
            )

        result.append(item)

    return result
