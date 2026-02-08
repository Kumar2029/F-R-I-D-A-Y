from core.domains import ActionDomain

class Goal:
    def __init__(self, name: str, target: str = None, content: str = None, domain: ActionDomain = None):
        self.name = name
        self.target = target
        self.content = content
        self.domain = domain
    
    def __repr__(self):
        return f"Goal(name='{self.name}', target='{self.target}', content='{self.content}', domain={self.domain})"
