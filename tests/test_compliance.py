import sys
import os
import unittest
import json

# Add project root to path
sys.path.append("/Users/aadityadevsharma/Documents/hackathon")

from src.agents.compliance_agent import run_compliance_audit

class TestComplianceAgent(unittest.TestCase):
    def test_run_audit(self):
        print("Starting compliance audit scanner test...")
        results = run_compliance_audit()
        
        # Verify schema
        self.assertIn("summary", results)
        self.assertIn("results", results)
        self.assertIn("latency", results)
        
        summary = results["summary"]
        print(f"\nAudit completed in {results['latency']:.2f} seconds.")
        print(f"Total Log Records Audited: {summary['total_scanned']}")
        print(f"Compliance Gaps Flagged: {summary['total_gaps']}")
        print(f"Critical Gaps: {summary['critical_gaps']}")
        print(f"Safety Score: {summary['safety_score_percentage']:.1f}%\n")
        
        for idx, res in enumerate(results["results"]):
            anomaly = res["anomaly"]
            audit = res["audit"]
            print(f"--- [Audit {idx+1}] {anomaly['id']} ({anomaly['source']}) ---")
            print(f"Type: {anomaly['type']}")
            print(f"Asset: {anomaly['asset']}")
            print(f"Violation: {'⚠️ Yes' if audit.get('violation_flag') else '✅ No'}")
            print(f"Severity: {audit.get('severity')}")
            print(f"Regulation Cited: {audit.get('regulations_cited')}")
            print(f"Assessment: {audit.get('audit_assessment')}")
            print(f"Remediation: {audit.get('remediation')}")
            print(f"Reporting Template:\n{audit.get('reporting_template')}\n")

if __name__ == "__main__":
    unittest.main()
