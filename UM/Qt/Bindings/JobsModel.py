from PyQt5.QtCore import Qt

from UM.JobQueue import JobQueue
from UM.Qt.ListModel import ListModel

class JobsModel(ListModel):
    IdRole = Qt.UserRole + 1
    DescriptionRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)

        jobQueue = JobQueue.getInstance()
        jobQueue.jobStarted.connect(self._onJobStarted)
        jobQueue.jobFinished.connect(self._onJobFinished)

        self._watchedJobIndices = {}

    def roleNames(self):
        return { self.IdRole: 'id', self.DescriptionRole: 'description', self.ProgressRole: 'progress' }

    def _onJobStarted(self, job):
        if job.isVisible():
            self.appendItem({ 'id': id(job), 'description': job.getDescription(), 'progress': -1 })
            job.progress.connect(self._onJobProgress)
            self._watchedJobIndices[job] = self.rowCount() - 1

    def _onJobProgress(self, job, progress):
        if job in self._watchedJobIndices:
            self.setProperty(self._watchedJobIndices[job], 'progress', progress)

    def _onJobFinished(self, job):
        if job in self._watchedJobIndices:
            self.removeItem(self._watchedJobIndices[job])
            job.progress.disconnect(self._onJobProgress)
            del self._watchedJobIndices[job]

