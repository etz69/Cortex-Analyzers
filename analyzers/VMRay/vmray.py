#!/usr/bin/env python
from cortexutils.analyzer import Analyzer
from vmrayclient import VMRayClient
from time import sleep


class VMRayAnalyzer(Analyzer):
    """
    VMRay analyzer that uses VMRayClient to connect to an VMRay instance. Allows uploading a sample and getting
    information via hash. More info regarding configuration in the complete documentation.
    """
    def __init__(self):
        Analyzer.__init__(self)
        self.url = self.getParam('config.url', None, 'No VMRay url given.').rstrip('/ ')
        disable_reanalyze = self.getParam('config.disablereanalyze', False)
        if disable_reanalyze == 'true' or disable_reanalyze:
            reanalyze = False
        else:
            reanalyze = True
        self.vmrc = VMRayClient(url=self.url,
                                key=self.getParam('config.key', None, 'No VMRay API key given.'),
                                cert=self.getParam('config.certpath', True),
                                reanalyze=reanalyze)

    def run(self):
        if self.data_type == 'hash':
            self.report({'scanreport': self.vmrc.get_sample(self.getData())})
        elif self.data_type == 'file':
            filepath = self.getParam('file')
            filename = self.getParam('filename')
            submit_report = self.vmrc.submit_sample(filepath=filepath,
                                                    filename=filename)
            # Check for completion
            while not self.vmrc.query_job_status(submissionid=submit_report['data']['submissions'][0]['submission_id']):
                sleep(10)

            # Return the results
            self.report({'scanreport': self.vmrc.get_sample(
                samplehash=submit_report['data']['submissions'][0]['submission_sample_sha256'])
            })
        else:
            self.error('Data type currently not supported')

    def summary(self, raw):
        result = {
            'reports': []
        }

        if raw.get('scanreport', None) and len(raw.get('scanreport').get('data')) > 0:
            for scan in raw.get('scanreport').get('data'):
                result['reports'].append({
                    'score': scan.get('sample_score'),
                    'sample_severity': scan.get('sample_severity'),
                    'sample_last_reputation_severity': scan.get('sample_last_reputation_severity'),
                    'url': scan.get('sample_webif_url')
                })
        return result

if __name__ == '__main__':
    VMRayAnalyzer().run()
