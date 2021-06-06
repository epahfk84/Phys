import FWCore.ParameterSet.Config as cms

isMC = False

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
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/2414AA91-A835-E311-97FA-003048F02C5E.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/241E1DD0-7435-E311-9F83-003048F1C1A2.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/244F2FEE-0D36-E311-AB4F-C86000151BE8.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/245E7F73-6E37-E311-A33D-003048FEC15C.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/246C457F-6B37-E311-9D26-003048F1C41C.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/2473F2E8-0D36-E311-A3CD-C860001BD8CA.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/2481639A-6D37-E311-9411-003048F0E552.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/248E3612-5935-E311-BBA5-003048F1E1E4.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/249AF3F2-0D36-E311-BA60-003048F24354.root',
    'file:/scratch/hdyoo/OpenData/samples/copy/Run2011B/15/24AA8D81-6A37-E311-B035-02163E008F58.root',
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
  fileName = cms.string('ntuple_skim_data.root')
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

process.p.remove(process.electronMatch)
process.p.remove(process.muonMatch)
