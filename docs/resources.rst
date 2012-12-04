Resources
=========

REST-style architectures consist of :doc:`clients` and servers. Clients 
initiate requests to servers; servers process requests and return appropriate 
responses. Requests and responses are built around the transfer of 
representations of :doc:`resources`. A resource can be essentially any coherent
and meaningful concept that may be addressed. A representation of a resource is
typically a document that captures the current or intended state of a resource.




If we always want to get the author indirectly via a ``Book`` resource, the 
``Author`` resource we defined at the start is not even required. Why not?

At the moment, RestORM does not automatically find your resources. They