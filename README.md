<html>
<head>
</head>

<body>

<h3>An Introduction To Corps Python</h3>
<p>
Corps Python is a proposed open-source software system currently being implemented to help developers create parallel
and distributed applications, services and microservices that seamlessly operate in heterogeneous multi/hybrid clouds,
at the edge, in on-premises data centers, on corporate PCs, etc - all at the same time.
<p><p>
Corps Python extends the Python language/platform while preserving its existing programming model of functions and
    class-based objects. It is a package written in standard Python and is fully compatible with it. Any host where Python runs
can run Corps Python.
</p>

<p>
If you are unfamiliar with Python see "Appendix A: Why Python?" below.
<p><p>
Python is a registered trademark of the Python Software Foundation.  The Corps Python Project is unaffiliated with the
Python Software Foundation and Corps Python is not a separate version of Python, but software built in it and for it.
<p><p>
For comments, inquiries, etc. please contact Corps Python Architect and Lead Engineer David Ayer at DavidAyer@CorpsPython.com.
</p>

<h4>Corps Python Fixes Python's Real Weaknesses</h4>

<p>While Python has numerous positive attributes it does have some trouble spots.  In the era of cloud computing,
    provisions for concurrency and utilizing multi-processor hosts and multiple hosts are most notably weak (if your
    first thought was Python's single processor performance see "Appendix A: Why Python?" below.).
<p><p>
  The existing solutions are low-level libraries for threads, processes, network stacks, etc., and most developers are
    uncomfortable with these.  They are tricky to use and are a departure from the objects and functions
they have expertise in.
<p><p>
Corps Python is a simple, comprehensive solution for concurrency, synchronization, parallelism, and distributed
    computations. It adds a small number of easy-to-use, but powerful, abstractions to Python, as well as a transparent
    run-time (operating) system.
<p><p>
Corps Python is designed to reduce the many traditional pain points in developing, deploying, and managing concurrent
programs in heterogeneous parallel and distributed contexts such as multiprocessor hosts and hybrid- and multi-cloud.
<p><p>
A Corps (a microservice, a service, an application, etc) is an asssemblage of Workers that are automatically created
and placed across the set of processors and hosts in a configuration.  All operations between the Workers are automatic
and transparent, even when the hosts are running different operating systems on different processor types.
<p><p>
And Corps are Workers also.  So a Corps can utilize other Corps and automatically interoperate with them.
<p><p>
Corps Python makes the underlying computational machinery (threads, processes, synchronization objects and operations,
network stacks, underlying operating system, processor types, etc.) disappear so developers can simply focus on program
functionality.
<p><p>
Software built using Corps Python is easy to deploy and manage for operations staff since they are self-monitoring,
self-healing, and self-scaling.  These capabilities can also be turned off so that external operating software such as
service mesh and container orchestration can be used.
</p>

<h4>A Better Alternative?</h4>

<p>But Corps Python may be a better alternative to high-complexity, high-overhead systems such as Istio and Kubernetes.
These were built for Google-scale services, are comprised of millions of lines of code, and result in high costs for
cloud resources and operational complexity.
<p><p>
Corps Python represents a middle ground between building a do-it-yourself system and the many development and deployment
    issues of contemporary software infrastructure.
<p><p>
Corps Python can act as an integrator, using Python as the unifying language of services and microservices while
    allowing the implementation of methods and functions to be done in the developers' preferred language via Python's
    "play nice with others" capabilities (and client-facing APIs can still utilize REST, JSON, etc.).
<p><p>
When completed Corps Python will only be on the order of hundreds of thousands of lines of code.  It's operating system
runs internally within each Corps and utilizes the power of Python to observe and direct run-time operations.  In most
circumstances it will run faster than current systems at a fraction of the operational complexity.
<p><p>
A Corps can be deployed to an arbitrary, heterogeneous configuration of hosts without changes to the source for
    different configurations or processor types or operating systems. And the same version of Corps Python's run-time
    system runs everywhere.
<p><p>
In contrast, running a major cloud vendor's cloud system requires different versions for their cloud, for on-premises
hosts, and at the edge.  Some require running only on approved on-premises server models.
<p><p>
Anywhere Python can run, Corps Python can run. So all of a company's often-idle machines, including PCs, could be
    utilized, thereby further saving on cloud costs.
</p>

<h4>Basic Computational Model</h4>

<p>Corps Python adds a small number of easy-to-use, but powerful, abstractions to Python, as well as a transparent
run-time system.
<p><p>
An individual Corps is an assemblage of Workers that can work independently or cooperatively to accomplish a task.
<p><p>
Workers can be built from regular class-based Python objects (Concs) or functions (Funcs), from previously-defined
Corps (Corps can be Workers external to the Corps or as contained, private, Workers), or custom-built from standard
Worker classes.
<p><p>
Each Corps is internally composed of a number of environments, or Envs, where Workers live and run.
<p><p>
The Envs are transparent to developers and are automatically created on the various hosts' processors by the Corps
Python runtime.
<p><p>
The Workers are automatically created and placed in the Envs and all operations between them are automatic and
transparent, even when the Workers are in different Envs on different hosts running different operating systems on
different processor types.
<p><p>
Regular Python methods and functions operate synchronously. The caller, running in a single thread, single process,
makes the call and the Python run-time pauses the caller until the return value has been produced by the method or
function.
<p><p>
But Corps Python's Workers can operate asynchronously from other Workers.
<p><p>
If a Worker asks another Worker to execute a method or function, the requesting Worker can do something else while the
servicing Worker accomplishes its task.
<p><p>
In fact it can ask many other servicing Workers to work concurrently.  And those Workers themselves may be composed of
many concurrently-operating Workers, and so on.
<p><p>
When the Workers are running on many processors on many hosts a high degree of parallelism can be achieved.
<p><p>
Corps Python automatically creates and sends the messages that pass between the Workers, schedules the Workers'
execution of the functions or methods, and returns the results back to the requesting Worker.
<p><p>
The calls to the Workers' methods and functions use the same syntax as regular Python objects' methods and
functions.
<p><p>
The developer just has to handle the asynchronously-returned result (which is fairly easy).
</p>

<h4>Corps Python's Advantages</h4>
<p>
In summary, why use Corps Python?
<p></p>
Consider the following advantageous features:
</p>
<ul>
    <li>Open source package that extends standard Python</li>
    <li>Simple, comprehensive solution for transparent concurrency on multiple processors on multiple hosts</li>
    <li>Self-monitoring, self-scaling, self-healing operations</li>
    <li>Deployment to dynamically-specified heterogeneous configurations</li>
    <li>Operates in today's microservices environments (Istio, Kubernetes, etc) or independently</li>
    <li>Interoperability and integration with the most-used languages (C, C++, Java, JavaScript, etc)</li>
    <li>Higher developer productivity</li>
    <li>Higher system performance</li>
    <li>Lower system complexity</li>
    <li>Lower development and operational costs</li>
</ul>

<h4>Further Reading</h4>
<ul>
    <li>All documentation is contained in the Doc directory.</li>
    <li>Status.txt summarizes the current project status.</li>
    <li>The Tutorials (Tutorial0.py, Tutorial1.py, etc) introduce the major Corps Python abstractions and demonstrate
    some important usage patterns.</li>
    <li>Roadmap.txt contains the current development tasks as well as a list of possible future initiatives.</li>
    <li>The Corps Python Reference, Reference.txt, is the definitive specification outside of the codebase for
    developer-facing functionality.</li>
    <li>The integration tests (CorpsPythonTest and CorpsTest0, 1, ...) in the Test directory attempt to vigorously exercise
    Corps Python functionality and can serve as further examples of feature usage.</li>
</ul>

<br>
<h4>Appendix A: Why Python?</h4>
<p>First, why use Python at all?
</p><p>
Well, there's much to love about Python:
</p>
<ul>
    <li>Easy to learn</li>
    <li>Minimal syntax</li>
    <li>Multi-paradigm</li>
    <li>Versatile</li>
    <li>Powerful</li>
    <li>High productivity</li>
    <li> Plays well with other languages and various hardware platforms and operating systems</li>
    <li>Mature</li>
    <li>Significant open-source ecosystem</li>
    <li>Large, friendly developer community</li>
    <li>Amongst the most-used languages world-wide</li>
</ul>

<p>But isn't Python slow? Straight out of the box, for some CPU-bound software, yes (this can be easily circumvented - see
below).
<p><p>
But most real-world software utilizes file systems and databases and networks.  These are two to three orders of
magnitude slower than CPU-based operations and there Python's performance isn't usually a cause of bottlenecks.
<p><p>
For CPU-bound software, Python methods and functions can be implemented in C or C++, and mechanisms are available to
access functions, methods, data, etc in much-used languages like Java and JavaScript.
<p><p>
This is why, for example, the popular, Python-based, deep neural-network package, PyTorch, is so performant - its
    mathematical base is written in C.
<p><p>
Usually only a small percentage of the code is responsible for the slowdown.  Identifying that code and replacing it is
generally a straightforward exercise in performance analysis and tuning.
</p>

<br><br>
</body>
</html>
