class CoordinatesTestPluginBase(TestPluginBase):
    package = 'q2_coordinates.tests'

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix='q2-coordinates-test-temp-')

    def tearDown(self):
        self.temp_dir.cleanup()

    def get_data_path(self, filename):
        return pkg_resources.resource_filename(self.package,
                                               'data/%s' % filename)

    def load_md(self, md_fn):
        md_fp = self.get_data_path(md_fn)
        sample_md = pd.read_csv(md_fp, sep='\t', header=0, index_col=0)
        return qiime2.Metadata(sample_md)

