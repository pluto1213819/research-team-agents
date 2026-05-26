"""
ResearchTeam Agents - Communication System
Agent间的消息传递与协调系统
"""

from typing import List, Dict, Any, Callable
from datetime import datetime
from collections import defaultdict
import json
import uuid


class Message:
    """消息对象"""
    
    def __init__(self, sender: str, receiver: str, content: str, msg_type: str = "text"):
        self.id = self._generate_id()
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.msg_type = msg_type
        self.timestamp = datetime.now().isoformat()
        self.metadata: Dict[str, Any] = {}
    
    def _generate_id(self) -> str:
        return str(uuid.uuid4())[:8]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.msg_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    def __str__(self):
        return f"[{self.sender} -> {self.receiver}] {self.content[:50]}..."


class MessageBus:
    """消息总线 - Agent间的通信中枢"""
    
    def __init__(self):
        self.message_queue: Dict[str, List[Message]] = defaultdict(list)
        self.message_history: List[Message] = []
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
    
    def send(self, message: Message):
        """发送消息"""
        self.message_queue[message.receiver].append(message)
        self.message_history.append(message)
        
        # 通知订阅者
        for callback in self.subscribers.get(message.receiver, []):
            callback(message)
        
        print(f"  [Message] {message.sender} -> {message.receiver}: {message.content[:40]}...")
    
    def receive(self, agent_name: str) -> List[Message]:
        """接收消息"""
        messages = self.message_queue.pop(agent_name, [])
        return messages
    
    def subscribe(self, agent_name: str, callback: Callable):
        """订阅消息"""
        self.subscribers[agent_name].append(callback)
    
    def get_history(self, agent_name: str = None) -> List[Dict]:
        """获取消息历史"""
        if agent_name:
            return [m.to_dict() for m in self.message_history 
                    if m.sender == agent_name or m.receiver == agent_name]
        return [m.to_dict() for m in self.message_history]
    
    def broadcast(self, sender: str, content: str, receivers: List[str]):
        """广播消息"""
        for receiver in receivers:
            msg = Message(sender, receiver, content, "broadcast")
            self.send(msg)


class ConversationThread:
    """对话线程 - 管理两个Agent间的对话"""
    
    def __init__(self, agent1: str, agent2: str, bus: MessageBus):
        self.agent1 = agent1
        self.agent2 = agent2
        self.bus = bus
        self.messages: List[Message] = []
    
    def add_message(self, sender: str, content: str) -> Message:
        """添加消息到线程"""
        receiver = self.agent2 if sender == self.agent1 else self.agent1
        msg = Message(sender, receiver, content)
        self.bus.send(msg)
        self.messages.append(msg)
        return msg
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取对话上下文"""
        return [
            {"role": "user" if m.sender == self.agent1 else "assistant", "content": m.content}
            for m in self.messages
        ]
