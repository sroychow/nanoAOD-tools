from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class lheWeightsFlattener(Module):
    def __init__(self):
        self.NumNNPDFWeights = 103
        self.NumScaleWeights = 18 # 18 for MiNNLO since it has NNPDF3.0 weights too, 9 for other samples
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.initReaders(inputTree)
        self.out.branch("scaleWeightMuR1MuF1", "F")
        self.out.branch("scaleWeightMuR1MuF2", "F")
        self.out.branch("scaleWeightMuR1MuF05", "F")
        self.out.branch("scaleWeightMuR05MuF1", "F")
        self.out.branch("scaleWeightMuR05MuF2", "F")
        self.out.branch("scaleWeightMuR05MuF05", "F")
        self.out.branch("scaleWeightMuR2MuF1", "F")
        self.out.branch("scaleWeightMuR2MuF2", "F")
        self.out.branch("scaleWeightMuR2MuF05", "F")

        for i in range(self.NumNNPDFWeights):
            self.out.branch("pdfWeightNNPDF%i" % i, "F")
        
    def initReaders(self, tree):
        self.LHEScaleWeight = tree.arrayReader("LHEScaleWeight")
        self.LHEPdfWeight = tree.arrayReader("LHEPdfWeight")
        self._ttreereaderversion = tree._ttreereaderversion
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        if event._tree._ttreereaderversion > self._ttreereaderversion:
            self.initReaders(event._tree)

        if len(self.LHEScaleWeight) < self.NumScaleWeights:
            raise RuntimeError("Found poorly formed LHE Scale weights")

        for i,varPair in enumerate([("05","05"), ("05","1"), ("05", "2"), ("1", "05"), \
                ("1","1"), ("1","2"), ("2", "05"), ("2", "1"), ("2", "2")]):
            self.out.fillBranch("scaleWeightMuR%sMuF%s" % varPair, self.LHEScaleWeight[i*2])

        if len(self.LHEPdfWeight) < self.NumNNPDFWeights:
            raise RuntimeError("Found poorly formed LHE Scale weights")

        for i in range(self.NumNNPDFWeights):
            self.out.fillBranch("pdfWeightNNPDF%i" % i, self.LHEPdfWeight[i])

        return True

flattenLheWeightsModule = lambda : lheWeightsFlattener() 
