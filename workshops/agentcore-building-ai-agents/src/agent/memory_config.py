import os
import uuid
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands.agent.conversation_manager import NullConversationManager, SlidingWindowConversationManager
from logger import get_logger

l = get_logger("memory_config")

MEMORY_ID = os.environ.get("MEMORY_ID")
l.info(f"ℹ️ MEMORY_ID={MEMORY_ID}")
ACTOR_ID = "customer-123"   # In production this comes from the authenticated user identity

def get_session_manager(session_id):
    if MEMORY_ID:
        memory_config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            batch_size=1,
            flush_interval_seconds=1,
            session_id=session_id, 
            actor_id=ACTOR_ID,
            retrieval_config={
                "support/customer/{actorId}/semantic/":     RetrievalConfig(top_k=3, relevance_score=0.2),
                "support/customer/{actorId}/preferences/":  RetrievalConfig(top_k=3, relevance_score=0.2),
            }
        )
        session_manager = AgentCoreMemorySessionManager(memory_config)
        l.info(f"✅ session_manager ready (MEMORY_ID={MEMORY_ID})")
        return session_manager
    else:
        l.info("⚠️ MEMORY_ID not set, session_manager disabled")    
        return None


