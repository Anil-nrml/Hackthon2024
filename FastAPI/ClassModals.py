from pydantic import BaseModel
class Modals:
    class AddSkillDetails(BaseModel):    
        SkillName: str = 'SkillName'
        SkillType: str = 'Soft Skill'
        SkillScore: int = 10   

    class FileDetails(BaseModel):
        filecontents: str
        IsJobDescription: bool
        filename: str
        fileid: str
        message: str
    class SkillDetails(BaseModel):
        skillid: int 
        requiredSkills: str
        softSkills: str
        goodToHaveSkills: str          