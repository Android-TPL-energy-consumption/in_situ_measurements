from Monsoon import sampleEngine, LVPM, pmapi
import Monsoon.Operations as op

from utils.settings import LVPMSerialNo, deviceVoltage


def setup_monsoon():
    """ Sets up Monsoon power monitor configuration.

    This configures Monsoon low-voltage power monitor (LVPM)[1] to provide some current on main channels to power tested
    phone.

    [1]: https://msoon.github.io/powermonitor/LVPM.html
    """
    monsoon = LVPM.Monsoon()
    monsoon.setup_usb(LVPMSerialNo, pmapi.USB_protocol())

    # Basic configuration.
    monsoon.fillStatusPacket()
    monsoon.setVout(deviceVoltage)
    engine = sampleEngine.SampleEngine(monsoon)

    # Disables console output.
    engine.ConsoleOutput(False)

    # Auto mode disables USB connection when sampling starts, and reactivates it when sampling ends.
    # It seems that Auto does not enable USB on launch, so you might need to play with the On value.
    # monsoon.setUSBPassthroughMode(op.USB_Passthrough.On)
    monsoon.setUSBPassthroughMode(op.USB_Passthrough.Auto)

    # Stop condition is time (will wait for a scenario to end).
    engine.setTriggerChannel(sampleEngine.channels.timeStamp)

    return engine

