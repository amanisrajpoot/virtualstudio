"""Skeleton Generator."""

class SkeletonGenerator:
    def generate(self, world_id: str, characters: list[str], goal_id: str, archetype_id: str) -> str:
        # A simple deterministic logic tree that blends goal and archetype
        c1 = characters[0] if characters else "Character 1"
        c2 = characters[1] if len(characters) > 1 else "Character 2"
        
        script = f"[{world_id.upper()}]\n\n"
        
        if goal_id == "sell_product":
            if archetype_id == "comedy":
                script += f"{c1} sets up a ridiculous stall.\n"
                script += f"{c2} approaches, looking extremely skeptical.\n"
                script += f"{c1} tries to sell them a clearly fake item with over-the-top promises.\n"
                script += f"{c2} laughs but ends up arguing about the price."
            elif archetype_id == "drama":
                script += f"{c1} is desperate to make a sale today.\n"
                script += f"{c2} arrives, looking for something specific.\n"
                script += f"{c1} offers a family heirloom out of desperation.\n"
                script += f"{c2} realizes the item's true value and a tense standoff begins."
            else:
                script += f"{c1} offers a product to {c2}.\nThey negotiate."
                
        elif goal_id == "argue":
            if archetype_id == "comedy":
                script += f"{c1} and {c2} bump into each other.\n"
                script += f"A petty argument breaks out over something completely trivial.\n"
                script += f"Things escalate to absurd levels quickly."
            else:
                script += f"{c1} confronts {c2} about a past betrayal.\n"
                script += f"The argument gets heated.\n"
                script += f"{c2} walks away."
                
        elif goal_id == "prank":
            script += f"{c1} sneaks up behind {c2}.\n"
            script += f"They execute a prank.\n"
            script += f"{c2} is shocked and reacts!"
            
        else:
            # Fallback
            script += f"{c1} and {c2} are present.\n"
            script += f"Goal: {goal_id}.\n"
            script += f"Style: {archetype_id}."
            
        return script
