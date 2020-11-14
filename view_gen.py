import torch
import numpy as np


def generate_views(B, N, P, I, view_chance=0.4, sabotage_chance=0.5):
    """
    INPUTS
        B: batch size
        N: number of events
        P: number of players
        I: number of players who are imposters
        view_chance: the chance of a player viewing another
        sabotage_change: the chance that an imposter sabotages in any given event

    OUTPUT
        tuple of (crew_views, imposter_views) of shapes
        (B, P - I, N, P+1) and (B, I, N, P+1) indicating the view of each
        crew member and imposter, where each player experiences N events.
        During each event they see some set of co-players, and sometimes
        experience/cause a sabotage.
    """

    assert P > I, "there must be more total players than imposters"

    # generate (B, N, P, P) symmetric matrix
    # [batch, events, viewee, viewer]
    groups = np.random.rand(B, N, P, P)
    groups = (groups + groups.transpose(0, 1, 3, 2)) / 2
    groups = groups < view_chance
    groups[:, :, np.arange(P), np.arange(P)] = True

    # (B, P - I) matrix representing the player indices
    players = np.random.rand(B, P).argsort(axis=1)
    imposters = players[:, :I]
    crew = players[:, I:]

    # (B, N, P) matrix representing who sabotages during each event
    sabotages = np.random.rand(B, N, P) < sabotage_chance
    sabotages[np.arange(B)[:, None], :, crew] = False

    # (B, N, 1, P) matrix representing who sees a sabotage
    see_sabotage = np.any(np.logical_and(groups, sabotages[:, :, :, None]), axis=2)[
        :, :, None, :
    ]

    views = np.logical_and(groups, np.logical_not(sabotages)[:, :, :, None])
    views[:, :, np.arange(P), np.arange(P)] = True
    views = np.concatenate((views, see_sabotage), axis=2)

    all_views = views.transpose(0, 3, 1, 2)
    crew_views = all_views[np.arange(B)[:, None], crew, :, :]
    imposter_views = all_views[np.arange(B)[:, None], imposters, :, :]

    return crew_views, imposter_views


def test():
    c, v = generate_views(2, 10, 5, 2)
    print(c.shape, v.shape)
    print("CREW VIEWS")
    print(c, end="\n\n")
    print("IMPOSTER VIEWS")
    print(v)


if __name__ == "__main__":
    test()
