import re
class SkillExtractorDetails:


    def GetSkillData(skill_extractor, inputData):
        skills_list = []
        annotations = skill_extractor.annotate(inputData)
        matches = annotations['results']['full_matches']+annotations['results']['ngram_scored']
        skills_list = []
        for result in matches:
            skill_id = result['skill_id']
            skill_name1 = skill_extractor.skills_db[skill_id]['skill_name']
            skill_name = skill_name1.split("(")[0].strip()
            skill_type = skill_extractor.skills_db[skill_id]['skill_type']
            skill_score = round(result['score'],2)
            if(skill_type != 'Soft Skill'):
                print(skill_name)
                if( skill_name in skills_list):
                    continue
                skills_list.append(skill_name)

        return skills_list        


    def extract_required_experience(job_description):
    # Define pattern for required experience using regular expression
        pattern = r"\b([0-9]+)\s?\+?\s?(?:years?|yrs?)\b"
        
        # Search for pattern in job description
        match = re.search(pattern, job_description, re.IGNORECASE)
        
        if match:
            required_experience = int(match.group(1))
            return required_experience
        else:
            return -1
