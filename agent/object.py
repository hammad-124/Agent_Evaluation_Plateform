from pydantic import BaseModel, Field


class Answer(BaseModel):
    answer:str = Field(description="The answer to the question of user.")
    conversation:bool = Field(description="Indicator to know that conversation should continue or not" \
                              " if agent has made dicision to refund then it shuold be fasle"\
                                "if agent has made dicision to continue conversation then it should be true", default=True)

class PurchaseItem(BaseModel):
    item_name:str = Field(description="Name of the item purchased by user.")
   