from Boid import Boid
from copy import deepcopy
from numpy import sign
import matplotlib.pyplot as plt


class Statistics:
    def __init__(self) -> None:
        self.turnSigma: float = 0.1
        self.minTurnDur: float = 0.1  # sec

        self._prevVel: dict[int, float] = {}
        self._turnAngleMap: dict[int, float] = {}
        self._turnDurMap: dict[int, float] = {}

        self.turnAngleLst: list[float] = []
        self.turnDurLst: list[float] = []

        self.caughtPrey: dict[int, int] = {}

    def reset(self):
        self.turnSigma: float = 0.1
        self.minTurnDur: float = 0.1  # sec

        self._prevVel: dict[int, float] = {}
        self._turnAngleMap: dict[int, float] = {}
        self._turnDurMap: dict[int, float] = {}

        self.turnAngleLst: list[float] = []
        self.turnDurLst: list[float] = []

        self.caughtPrey: dict[int, int] = {}

    def _initVars(self, boid: Boid):
        ID = boid.getId()
        if ID not in self._prevVel:
            self._prevVel[ID] = deepcopy(boid.getVelocity())
        if ID not in self._turnDurMap:
            self._turnDurMap[ID] = 0
        if ID not in self._turnAngleMap:
            self._turnAngleMap[ID] = 0

    def _addTurn(self, boid: Boid):
        ID = boid.getId()
        self.turnDurLst.append(self._turnDurMap[ID])
        self.turnAngleLst.append(abs(self._turnAngleMap[ID]))

    def _detectTurn(self, boid: Boid, dt: float):
        ID = boid.getId()

        angle = boid.getVelocity().angle_to(self._prevVel[ID])
        dur = self._turnDurMap[ID]
        if (abs(angle) < self.turnSigma) or (
            (sign(self._turnAngleMap[ID]) != 0)
            and (sign(angle) != sign(self._turnAngleMap[ID]))
        ):
            if dur > self.minTurnDur:
                self._addTurn(boid)
            self._turnDurMap[ID] = 0
            self._turnAngleMap[ID] = 0
        else:
            self._turnAngleMap[ID] += angle
            self._turnDurMap[ID] += dt

        self._prevVel[ID] = deepcopy(boid.getVelocity())

    def update(
        self,
        step: int,
        friendlies: list[Boid],
        enemies: list[Boid],
        n_prey_caught: int,
        dt: float,
    ):
        if n_prey_caught > 0:
            self.caughtPrey[step] = n_prey_caught

        for f in friendlies:
            self._initVars(f)
            self._detectTurn(f, dt)

    def _plotTurnDurFreq(self, stepNo: int):
        fig, axs = plt.subplots(1, 1, tight_layout=True)
        axs.hist(self.turnDurLst, bins=100)
        axs.set_xlabel("Turn duration (s)")
        axs.set_ylabel("Frequency")
        # fig.savefig(f"turn_dur_freq_{stepNo}.pdf")
        fig.show()

    def _plotTurnAngleFreq(self, stepNo: int):
        fig, axs = plt.subplots(1, 1, tight_layout=True)
        axs.hist(self.turnAngleLst, bins=100)
        axs.set_xlabel("Turn angle (deg)")
        axs.set_ylabel("Frequency")
        # fig.savefig(f"turn_angle_freq_{stepNo}.pdf")
        fig.show()

    def _plotTurnAngleDur(self, stepNo: int):
        fig, axs = plt.subplots(1, 1, tight_layout=True)
        axs.scatter(self.turnDurLst, self.turnAngleLst)
        axs.set_xlabel("Turn duration (s)")
        axs.set_ylabel("Turn angle (deg)")
        # fig.savefig(f"turn_angle_dur_{stepNo}.pdf")
        fig.show()

    def _plotPredatorAttackSuccess(self, stepNo: int):
        fig, axs = plt.subplots(1, 1, tight_layout=True)
        plt.hist(
            x=self.caughtPrey.keys(),
            weights=self.caughtPrey.values(),
            bins=list(range(stepNo + 1)),
            cumulative=True,
        )
        axs.set_xlabel("Simulation step")
        axs.set_ylabel("Caught prey (cumulative)")
        fig.show()

    def plotResults(self, stepNo: int):
        self._plotTurnDurFreq(stepNo)
        self._plotTurnAngleFreq(stepNo)
        self._plotTurnAngleDur(stepNo)
        self._plotPredatorAttackSuccess(stepNo)
