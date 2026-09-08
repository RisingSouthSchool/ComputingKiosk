from functions import main

main()

# # Card display
# def drawing_card(card):
#     rank, suit = card
#     return [
#         "┌─────────┐",
#         f"│{rank:<2}       │",
#         "│         │",
#         f"│    {suit}    │",
#         "│         │",
#         f"│       {rank:>2}│",
#         "└─────────┘"
#     ]

# # Hidden card
# def hidden_card():
#     return [
#         "┌─────────┐",
#         "|         |",
#         "|         |",
#         "|         |",
#         "|         |",
#         "|         |",
#         "└─────────┘"
#     ]

# # Print cards side by side
# def print_cards(cards, hide_second=False):
#     card_lines = []

#     for i, card in enumerate(cards):
#         if hide_second and i == 1:
#             card_lines.append(hidden_card())
#         else:
#             card_lines.append(drawing_card(card))

#     for i in range(7):
#         for card in card_lines:
#             print(card[i], end="  ")
#         print()