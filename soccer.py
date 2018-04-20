import numpy as np
from termcolor import colored


class SoccerGame:

    def __init__(self):
        self.state = np.zeros([3,2]) # A pos, B pos, Possession
        self.a_goal = np.array([
            [0, 0],
            [1, 0],
        ])
        self.b_goal = np.array([
            [0, 3],
            [1, 3],
        ])
        self.state_shape = [2, 4, 2, 4, 2] # board size (two players), possession
        self.action_size = 5

    def reset(self, force_state=None):
        if force_state == None:
            # randomize initial a position
            # either (1, 0) or (1, 1)
            self.players = np.array([
                [np.random.randint(0, 2), 1],
                [np.random.randint(0, 2), 2]
            ])

            # randomise inital possession
            # 0 - A possession
            # 1 - B possession
            self.possession = np.random.randint(0, 2)

        else:
            [a_y, a_x, b_y, b_x, possession] = force_state
            self.players = np.array([
                [a_x, a_y],
                [b_y, b_x]
            ])
            self.possession = possession


        # return state
        self.done = False
        return self.get_state()


    def get_state(self):
        """
        return the current sate
        """
        return np.array([
            self.players[0],
            self.players[1],
            np.array([self.possession, 0])
        ])

    def map_action_to_change(self, action):
        return {
            0: np.array([0, 1]), # north
            1: np.array([1, 0]), # east
            2: np.array([0, -1]), # south
            3: np.array([-1, 0]), # south
            4: np.array([0, 0]) # stick
        }.get(action)

    def step(self, action_vec, doPrint=True):
        """
        take step randomizing the order of the actions

        # Scoring
        # player with ball moves into goal
        # 1. is opponent goal (scorer +100, other -100)
        # 2. is own goal (scorer -100, other +100)


        # If sequence causes players to collide
        # 1. Only the first mover moves, other sticks
        # 2. If the one with the ball moves second, then the ball changes posetion

        action_vec - n vector of actions (n is number of players - or 2)
        """
        if self.done:
            return
        order = np.array([0, 1])
        np.random.shuffle(order)
        reward = np.array([0, 0])
        old_players = [[], []]

        for order_idx, idx in enumerate(order):
            old_players[idx] = np.copy(self.players[idx])
            self.players[idx] = np.clip(
                self.players[idx] + self.map_action_to_change(action_vec[idx]),
                [0, 0],
                [1, 3]
            )
            # crashing into the wall is the same as sticking
            if np.all(self.players[idx] == old_players[idx]):
                action_vec[idx] = 4

        # check collision
        if np.all(self.players[0] == self.players[1], axis=0):
            if doPrint:
                print("collision!", order, action_vec)
                self.print()
                print("collision!", order, action_vec)
            first = order[0]
            second = order[1]
            # first mover has ball, second sticks
            if first == self.possession:
                # second user stick
                if action_vec[second] == 4:
                    # first goes back
                    self.players[first] = old_players[first]
                    # change possession
                    self.possession = second
                else:
                    # second goes back
                    self.players[second] = old_players[second]
            # second mover has ball
            else:
                # second mover stick
                if action_vec[second] == 4:
                    # first goes back
                    self.players[first] = old_players[first]
                else:
                    # second goes back
                    self.players[second] = old_players[second]
                    # change possession
                    self.possession = first

        # check goals
        # in a goal
        if np.any(np.all(self.a_goal == self.players[self.possession], axis=0)):
            self.done = True
            reward[0] = -100
            reward[1] = 100
            return [
                self.get_state(),
                reward,
                self.done
            ]

        # in b goal
        if np.any(np.all(self.b_goal == self.players[self.possession], axis=0)):
            self.done = True
            reward[0] = 100
            reward[1] = -100

        if doPrint:
            self.print()

        return [
            self.get_state(),
            reward,
            self.done
        ]

    def print(self):
        a_pos = self.players[0]
        b_pos = self.players[1]

        grid = [
            ['   ', '   ', '   ', '   '],
            ['   ', '   ', '   ', '   ']
        ]

        # set goals to green
        grid[self.a_goal[0, 0]][self.a_goal[0, 1]] = colored(' A ', 'green', attrs=['reverse'])
        grid[self.a_goal[1, 0]][self.a_goal[1, 1]] = colored(' A ', 'green', attrs=['reverse'])
        grid[self.b_goal[0, 0]][self.b_goal[0, 1]] = colored(' B ', 'green', attrs=['reverse'])
        grid[self.b_goal[1, 0]][self.b_goal[1, 1]] = colored(' B ', 'green', attrs=['reverse'])

        ball_text = ' ⚽ '

        # set player position
        if np.all(a_pos == b_pos):
            grid[a_pos[0]][a_pos[1]] = colored(ball_text, 'magenta', attrs=['reverse'])
        else:
            if self.possession == 0:
                a_text = ball_text
                b_text = '   '
            else:
                a_text = '   '
                b_text = ball_text
            grid[a_pos[0]][a_pos[1]] = colored(a_text, 'red', attrs=['reverse'])
            grid[b_pos[0]][b_pos[1]] = colored(b_text, 'blue', attrs=['reverse'])

        for row in grid:
            print('\n', end='')
            for cell in row:
                print(cell, end='')
        print('\n')
