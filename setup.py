from setuptools import setup, find_packages

setup(
    name="agentmagnet-mcp",
    version="2.0.0",
    description="AgentMagnet: Universal Agent Commerce Layer. AI agents search products across 20+ stores worldwide.",
    long_description="AgentMagnet is an MCP server that lets AI agents search products across Amazon (12 countries), eBay (7 countries), AliExpress, SaaS platforms, and B2B industrial programs. Supports x402 micro-payments, 14 languages, agent referral system, and generates affiliate commissions automatically — all machine-to-machine.",
    author="AgentMagnet",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "anyio>=4.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "agentmagnet=agentmagnet.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Framework :: MCP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    ],
)
