const hre = require("hardhat");

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);

    // 1. Deploy ModuleRegistry
    const ModuleRegistry = await hre.ethers.getContractFactory("ModuleRegistry");
    const moduleRegistry = await ModuleRegistry.deploy();
    await moduleRegistry.waitForDeployment();
    const moduleRegistryAddress = await moduleRegistry.getAddress();
    console.log("ModuleRegistry deployed to:", moduleRegistryAddress);

    // 2. Deploy EscrowCore (arbitrator is deployer for now)
    const EscrowCore = await hre.ethers.getContractFactory("EscrowCore");
    // We'll update the marketplace kernel address after its deployment
    const escrowCore = await EscrowCore.deploy(deployer.address, deployer.address);
    await escrowCore.waitForDeployment();
    const escrowCoreAddress = await escrowCore.getAddress();
    console.log("EscrowCore deployed to:", escrowCoreAddress);

    // 3. Deploy MarketplaceKernel
    const MarketplaceKernel = await hre.ethers.getContractFactory("MarketplaceKernel");
    const kernel = await MarketplaceKernel.deploy(moduleRegistryAddress, escrowCoreAddress, deployer.address);
    await kernel.waitForDeployment();
    const kernelAddress = await kernel.getAddress();
    console.log("MarketplaceKernel deployed to:", kernelAddress);

    // 4. Deploy Prototype Modules
    const ProductModule = await hre.ethers.getContractFactory("ProductModule");
    const productModule = await ProductModule.deploy(kernelAddress, escrowCoreAddress);
    await productModule.waitForDeployment();
    const productModuleAddress = await productModule.getAddress();
    console.log("ProductModule deployed to:", productModuleAddress);

    const ServiceModule = await hre.ethers.getContractFactory("ServiceModule");
    const serviceModule = await ServiceModule.deploy(kernelAddress, escrowCoreAddress);
    await serviceModule.waitForDeployment();
    const serviceModuleAddress = await serviceModule.getAddress();
    console.log("ServiceModule deployed to:", serviceModuleAddress);

    // 5. Setup Permissions
    console.log("Configuring protocol permissions...");

    // Register modules in the registry
    await moduleRegistry.approveModule(productModuleAddress, "ipfs://product-module-metadata");
    await moduleRegistry.approveModule(serviceModuleAddress, "ipfs://service-module-metadata");

    const addresses = {
        kernel: kernelAddress,
        moduleRegistry: moduleRegistryAddress,
        escrowCore: escrowCoreAddress,
        productModule: productModuleAddress,
        serviceModule: serviceModuleAddress
    };

    const fs = require("fs");
    const path = require("path");
    const frontendDir = path.join(__dirname, "../../frontend/dashboard/src/constants");
    if (!fs.existsSync(frontendDir)) {
        fs.mkdirSync(frontendDir, { recursive: true });
    }
    fs.writeFileSync(
        path.join(frontendDir, "addresses.json"),
        JSON.stringify(addresses, null, 2)
    );

    console.log("Addresses saved to frontend.");
    console.log("Deployment and configuration complete.");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
