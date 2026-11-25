# PAC3220 → WinCC V7.3 OPC DA Gateway

## Architecture
PAC3220 Modbus TCP → existing Python Modbus/decoder modules → OpenOPC-DA
client → local WinCC OPC DA server (`OPCServer.WinCC`) → WinCC internal tags.

This project is an OPC DA **client**. WinCC Runtime provides the OPC DA server.

## 1. WinCC preparation
1. Open the correct WinCC V7.3 project in WinCC Explorer.
2. Create internal tags whose names exactly match the names in `pac3220/tags.py`.
3. Use a 32-bit floating-point/Float data type for these PAC measurements.
4. Also create `PY_TEST` as an internal Float tag for the initial write test.
5. Activate WinCC Runtime. The WinCC OPC DA server is `OPCServer.WinCC`.
6. Local WinCC tag ItemIDs are the tag names themselves (no server prefix).

Siemens reference: WinCC V7 OPC DA server ProgID is `OPCServer.WinCC`; the
WinCC project must be enabled/active for its OPC process data to be available.

## 2. Python compatibility and dependencies
OPC DA uses Windows COM/DCOM. Run this project on the same Windows PC as WinCC.
Use a supported Windows Python installation (recommend Python 3.11 or 3.12)
and ensure the OPC Automation wrapper DLL and Python process have compatible
bitness. The OpenOPC-DA package requires a registered OPC DA Automation wrapper.

From an elevated or normal CMD as appropriate for your IT policy:

```cmd
cd /d D:\pac3320_gateway
python -m pip install -r requirements.txt
```

If your existing gateway Python is 3.15, do not assume the legacy COM stack is
qualified for it. Install Python 3.11/3.12 x64 in a separate environment if
required, then install the requirements there. Do not uninstall the working
Modbus Python environment until the OPC DA test passes.

## 3. Test a single write before the gateway
```cmd
python test_opc_da.py
```
Expected: write of `123.45` to `PY_TEST`, read-back quality `Good`, and
read-back value `123.45`. If it fails, check WinCC Runtime, server ProgID,
OPC Automation wrapper registration, Python bitness, and DCOM permissions.

## 4. Run the gateway
```cmd
python main.py
```
The gateway reads the configured Modbus blocks and writes values to matching
WinCC ItemIDs. The OPC DA connection is created once and retried after failure.

## 5. Important register caution
`Tariff_1_Import_kWh` and `Tariff_1_Import_kVARh` are marked unverified because
the earlier meter output was implausibly large. They are skipped from WinCC writes
by default (`OPC_DA_SKIP_UNVERIFIED_TAGS = True` in `pac3220/config.py`).
Validate their register map, Float32/64 type, word order and scaling against the
meter display before enabling these two writes.

## 6. Operational cautions
- First test only with `PY_TEST` and read-only/non-actuating internal measurement tags.
- Do not use this client to write PLC control outputs or safety-related tags.
- OPC DA DCOM permissions and Windows firewall/security policy must be approved
  by your OT/IT administrator.
- The OPC DA server being available does not prove every ItemID is valid; check
  per-item write status and read back values in WinCC/OPC client.
