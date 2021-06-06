import FWCore.ParameterSet.Config as cms

isMC = True

process = cms.Process("DYSkim")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")

## Options and Output Report
process.options   = cms.untracked.PSet( 
  wantSummary = cms.untracked.bool(True) 
)
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
SkipEvent = cms.untracked.vstring('ProductNotFound')

## Source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
    # replace below link by your input files
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/1630D3E8-1AC6-E311-8675-001E67397D55.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/1633B072-1AC6-E311-8951-001E67396D42.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/16448807-15C6-E311-97B3-001E67396DBA.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/164E73DF-E6C2-E311-B0B2-001E67396BA3.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/165B9D93-2BC5-E311-92A0-0025B3E063A8.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/1669AFDF-E6C5-E311-9C8E-001E67397391.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/16751CB6-2AC4-E311-8C0B-001E67397D5A.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/169835E7-FCC5-E311-A2A8-002590A3C992.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/16A3FFB5-18C5-E311-9AAF-001E67396E05.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/DY/15/16B1860E-27C4-E311-A47B-002590200A80.root',
    )
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

## Geometry and Detector Conditions (needed for a few patTuple production steps)
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = cms.string('GR_R_53_V16::All')

process.load("Configuration.StandardSequences.MagneticField_cff")

## Output Module Configuration (expects a path 'p')
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('patTuple_skim.root'),
    splitLevel = cms.untracked.int32(0),
    # save only events passing the full path
    #SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    # save PAT Layer 1 output; you need a '*' to
    # unpack the list of commands 'patEventContent'
    outputCommands = cms.untracked.vstring('drop *')
)

import HLTrigger.HLTfilters.hltHighLevel_cfi
process.dimuonsHLTFilter = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()

process.dimuonsHLTFilter.TriggerResultsTag = cms.InputTag("TriggerResults","","HLT")
process.dimuonsHLTFilter.HLTPaths = ["HLT_Mu*","HLT_DoubleMu*","HLT_IsoMu*"]

process.TFileService = cms.Service("TFileService",
  fileName = cms.string('ntuple_skim_dy.root')
)

process.goodOfflinePrimaryVertices = cms.EDFilter("VertexSelector",
   src = cms.InputTag("offlinePrimaryVertices"),
   cut = cms.string("!isFake && ndof > 4 && abs(z) < 24 && position.Rho < 2"), # tracksSize() > 3 for the older cut
   filter = cms.bool(True),   # otherwise it won't filter the events, just produce an empty vertex collection.
)

process.noscraping = cms.EDFilter("FilterOutScraping",
   applyfilter = cms.untracked.bool(True),
   debugOn = cms.untracked.bool(False),
   numtrack = cms.untracked.uint32(10),
   thresh = cms.untracked.double(0.25)
)

process.FastFilters = cms.Sequence( process.goodOfflinePrimaryVertices + process.noscraping )

from Phys.DYntupleMaker.DYntupleMaker_cfi import *
from Phys.DYntupleMaker.DYntupleMaker_cfi import *

process.recoTree = DYntupleMaker.clone()
process.recoTree.isMC = isMC
process.recoTree.Muon = "patMuons"

# load the PAT config
process.load("PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff")

from PhysicsTools.PatAlgos.patEventContent_cff import *
process.out.outputCommands += patTriggerEventContent
process.out.outputCommands += patExtraAodEventContent
process.out.outputCommands += patEventContentNoCleaning
process.out.outputCommands.extend(cms.untracked.vstring(
  'keep *_*_*_*',
))

# Let it run
process.p = cms.Path(
  process.FastFilters *
  process.patCandidates *
  # process.patDefaultSequence
  process.recoTree
)
process.p.remove(process.makePatPhotons)
process.p.remove(process.makePatJets)
process.p.remove(process.makePatTaus)
process.p.remove(process.makePatMETs)
process.p.remove(process.patCandidateSummary)

#not for MC	
#process.p.remove(process.electronMatch)
#process.p.remove(process.muonMatch)
