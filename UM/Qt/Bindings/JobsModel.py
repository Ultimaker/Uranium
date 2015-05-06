# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import Qt

from UM.JobQueue import JobQueue
from UM.Qt.ListModel import ListModel
from UM.Application import Application

class JobsModel(ListModel):
    IdRole = Qt.UserRole + 1
    DescriptionRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)

        jobQueue = JobQueue.getInstance()
        jobQueue.jobStarted.connect(self._onJobStarted)
        jobQueue.jobFinished.connect(self._onJobFinished)

        self._watched_job_indices = {}
        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.ProgressRole, "progress")

    def _onJobStarted(self, job):
        if job.isVisible():
            self.appendItem({ "id": id(job), "description": job.getDescription(), "progress": -1 })
            job.progress.connect(self._onJobProgress)
            self._watched_job_indices[job] = self.rowCount() - 1

    def _onJobProgress(self, job, progress):
        if job in self._watched_job_indices:
            self.setProperty(self._watched_job_indices[job], "progress", progress)

    def _onJobFinished(self, job):
        if job in self._watched_job_indices:
            self.removeItem(self._watched_job_indices[job])
            job.progress.disconnect(self._onJobProgress)
            del self._watched_job_indices[job]

