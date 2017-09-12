import ingestor

class DpxClientPlate(ingestor.Crawler.Fs.Image.Dpx):
    """
    Custom crawler to detect dpx plates delivered by the client.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a DpxClientPlate object.
        """
        super(DpxClientPlate, self).__init__(*args, **kwargs)

        # parsing shot and sequence from the name
        nameParts = self.var('name').split('_')
        seq = 'EP{0}'.format(nameParts[0][3:])
        self.setVar('seq', seq)
        self.setVar(
            'shot',
            'HVN-{0}-{1}-{2}'.format(
                seq,
                nameParts[1],
                nameParts[2]
            ),
        )

        # the plate name is hard-coded as plate which is used for the
        # detection by the test
        self.setVar('plateName', 'plate')

        # plate has the image sequence format:
        # 'XHE102_013_010_plate.1084.dpx'
        if self.var('imageType') == 'sequence':

            # setting version 0, since it is not part of the file name
            self.setVar('version', 0)

        # otherwise plate has the image sequence format:
        # 'XHE102_013_060_plate_v00200986.dpx'
        else:
            versionDigits = 4 # v002
            version = int(nameParts[-1][1: versionDigits])
            frame = nameParts[-1][versionDigits:]

            self.setVar('name', '_'.join(nameParts[: -1]))
            self.setVar('version', version)
            self.setVar('frame', int(frame))
            self.setVar('padding', len(frame))
            self.setVar('imageType', 'sequence')

    @classmethod
    def test(cls, pathHolder, parentCrawler):
        """
        Test if the path holder contains an dpx plate file.
        """
        if not super(DpxClientPlate, cls).test(pathHolder, parentCrawler):
            return False

        baseName = pathHolder.baseName()
        return ('_plate.' in baseName or '_plate_' in baseName)


# registering crawler
DpxClientPlate.register(
    'dpxClientPlate',
    DpxClientPlate
)
