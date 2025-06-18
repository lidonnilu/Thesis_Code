from nomad.config.models.plugins import SchemaPackageEntryPoint


class pld_schemaEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_plugin_pld_moda.schema_packages.pld_schema import m_package

        return m_package


pld_schema_entry_point = pld_schemaEntryPoint(
    name='PLD-MODA-LAB',
    description='Schema package for the description of the PLD-MODA instrument of the MODA laboratory of the CNR-SPIN of Naples.',
)
