# Introduction

The ArtifactDB framework originated within the Genomics Platform, here at Genentech. Main use cases were about
supporting data and metadata management of genomics datasets, in a cloud-based approach. ArtifactDB clients have been
developed with the purpose of providing bioinformaticians and computional biologists a convenient way to access these
datasets, with the tools they are the most familiar with: R session, RStudio, Jupyter notebooks, etc... that is,
analytical environments, close to scientific use cases.

These clients provide not only access to the data and metadata by interfacing with ArtifactDB REST API endpoints on the
backend side, but also manage the data model and its representation in the context of these analytical environments. For
instance, `dsassembly` handles the conversion between a Multi Assay Experiment (MAE), an in-memory R structure, and its
"deconstructed" equivalent found in an ArtifactDB instance.

In the process of building these rich, heavy and sophisticated clients, a generic use case has fallen between the
cracks: accessing an ArtifactDB instance in the most simplest and direct approach, from our beloved terminal. The
ArtifactDB Command Line Interface (CLI) goal is to bridge that gap[^1], by providing an easy way to connect to any
ArtifactDB instances and perform common operations such as searching metadata, uploading and downloading projects,
managing permissions, etc...

Who should use ArtifactDB CLI? Anyone who needs to access an ArtifactDB instance at a low level, ie. not necessarily
from an analytical environments where these heavy clients mentioned above are more suitable. The CLI is a convenient way
to prototype, interface with an instance, on a file by file basis. Storing and managing individual artifacts is a
generic and very simple use case, yet very useful, and possibly constituting a first step in maturing an instance later
with a more advanced, specialized client.

[^1]: The presence of Iris, goddess of the rainbow, found on the cover of this document, is not a random choice. Iris is
  also responsible for carrying the water of the River Styx to Olympus (aka the Self Service component of the ArtifactDB
  platform). The Greek mythology mentions the water would render unconscious for one year any god or goddess who lied.
  I'm still not sure what this could mean in this context...

