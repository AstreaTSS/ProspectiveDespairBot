import disnake
from rapidfuzz import fuzz
from rapidfuzz import process

import common.cards as cards


async def extract_from_list(
    inter: disnake.ApplicationCommandInteraction,
    argument,
    list_of_items,
    processors,
    score_cutoff=0,
):
    """Uses multiple scorers and processors for a good mix of accuracy and fuzzy-ness"""
    combined_list = []

    scorers = (fuzz.token_set_ratio, fuzz.WRatio)
    for scorer in scorers:
        for processor in processors:
            fuzzy_list = process.extract(
                argument,
                list_of_items,
                scorer=scorer,
                processor=processor,
                score_cutoff=score_cutoff,
            )
            if fuzzy_list:
                combined_entries = [e[0] for e in combined_list]

                if (
                    processor == fuzz.WRatio
                ):  # WRatio isn't the best, so we add in extra filters to make sure everythings turns out ok
                    new_members = [
                        e
                        for e in fuzzy_list
                        if e[0] not in combined_entries
                        and (len(processor(e[0])) >= 2 or len(argument) <= 2)
                        and argument.lower() in processor(e[0])
                    ]

                else:
                    new_members = [
                        e
                        for e in fuzzy_list
                        if e[0] not in combined_entries
                        and argument.lower() in processor(e[0])
                    ]

                combined_list.extend(new_members)

    return combined_list


def get_card_name(card):
    if isinstance(card, cards.Card):
        return card.oc_name.lower()
    else:
        return card


async def extract_cards(inter: disnake.ApplicationCommandInteraction, argument):
    queried_cards: list[list[cards.Card]] = await extract_from_list(
        inter,
        argument.lower(),
        tuple(cards.participants + cards.hosts),
        [get_card_name],
    )
    return [c[0].oc_name for c in queried_cards]
