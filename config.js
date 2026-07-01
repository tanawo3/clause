// Clause configuration. In this static stack this module stands in for build-time values.
export const CONTRACT = "0x43D229F781dC44758A45FB683c4c785500769010";
export const NETWORK = "studionet";
export const CHAIN_ID = "0xf22f";
export const EXPLAINER_DOC = "https://docs.genlayer.com/";
// Demo mode is on only when no valid contract address is configured. It never
// pretends to be a real on-chain interaction.
export const DEMO = !/^0x[0-9a-fA-F]{40}$/.test(CONTRACT);
