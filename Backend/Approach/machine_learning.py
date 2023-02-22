import numpy as np

class QLearningAgent:
    def __init__(self, n_states, n_actions, alpha, gamma, epsilon):
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = np.zeros((n_states, n_actions))

    def get_action(self, state):
        if np.random.uniform(0, 1) < self.epsilon:
            # Explore by taking a random action
            action = np.random.randint(self.n_actions)
        else:
            # Exploit by taking the action with the highest Q-value
            action = np.argmax(self.Q[state, :])
        return action

    def update(self, state, action, reward, next_state, done):
        # Update Q-value for the current state and action
        max_next_Q = np.max(self.Q[next_state, :])
        td_target = reward + self.gamma * max_next_Q * (1 - done)
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

n_states = 10
n_actions = 2
alpha = 0.5
gamma = 0.9
epsilon = 0.1
agent = QLearningAgent(n_states, n_actions, alpha, gamma, epsilon)
for i in range(1000):
    action = agent.get_action(state)
    reward = 1
    next_state = 1
    done = False
    agent.update(state, action, reward, next_state, done)