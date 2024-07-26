Hiring Manager Guidance:
- We are deciding whether to proceed to the 'Technical Phase' or follow up with the 'Starting Phase'
- Process the conversation carefully
- Focus on the last Politeness score

Output requirement:
- Must focus on the Politeness score and return a message conforming to the below logic:
---
if Politeness is less than 50:
    encourage the candidate to adjust their tone
else:
    just single word "technical_phase"

Examples:

Politeness = 49

Answer: I appreciate your candor, but I'd like to encourage you to consider how your tone might be perceived by others.
 Using more polite language can help foster a more positive and productive environment for everyone involved.

Politeness = 70

Answer: technical_phase

Politeness = 90

Answer: technical_phase

Politeness = 30

Answer: I appreciate your directness, but let's try to maintain a respectful and professional tone throughout our conversation.
 Could you please rephrase that in a more polite manner?

Politeness = /* infer the value from the last evaluation */

Answer: 