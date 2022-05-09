#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/types.h>
#include <asm/io.h>
#include <linux/loop.h>

#define LegionControllerVer "V0.3"

struct DEVICE_DATA
{
    uint64_t baseEC;
    uint16_t fanSpeedCurrent;
    uint16_t tempCurrentCPU; // CPU temp
    uint16_t tempCurrentGPU; // GPU temp
    uint16_t fanCurve[22];
    uint8_t curveLen;
    uint8_t powerMode;
};

struct DEVICE_DATA GKCN =
    {
        .baseEC = 0xFE00D400,     // need to start at EC level
        .fanSpeedCurrent = 0x200, // 0x1FC
        .tempCurrentCPU = 0x138,
        .tempCurrentGPU = 0x139,
        .fanCurve = {0x140, 0x141, 0x142, 0x143, 0x144, 0x145, 0x146, 0x147, 0x148, 0x149, 0x14A, 0x150, 0x151, 0x152, 0x153, 0x154, 0x155, 0x156, 0x157, 0x158, 0x159, 0x15A},
        .curveLen = 22,
        .powerMode = 0x20,

};

uint8_t *virt;
int i, pFanCurve;

static int cPowerMode = -1;
static int cFanCurve = -1;

module_param(cPowerMode, int, 0644);
module_param(cFanCurve, int, 0644);

struct DEVICE_DATA *dev_data;

static struct kobject *LegionController;
static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);
void writeFanCurve(void);
void writePowerMode(void);

struct kobj_attribute fanSpeedCurrent = __ATTR(fanSpeedCurrent, 0444, sysfs_show, NULL);
struct kobj_attribute tempCurrentCPU = __ATTR(tempCurrentCPU, 0444, sysfs_show, NULL);
struct kobj_attribute tempCurrentGPU = __ATTR(tempCurrentGPU, 0444, sysfs_show, NULL);
struct kobj_attribute fanCurve = __ATTR(fanCurve, 0444, sysfs_show, NULL);
struct kobj_attribute powerMode = __ATTR(powerMode, 0444, sysfs_show, NULL);

static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    if (attr == &fanSpeedCurrent)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->fanSpeedCurrent));
    }
    if (attr == &tempCurrentCPU)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->tempCurrentCPU));
    }
    if (attr == &tempCurrentGPU)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->tempCurrentGPU));
    }

    if (attr == &powerMode)
    {
        writePowerMode();
        
        writeFanCurve();

        
        if (*(virt + dev_data->powerMode) == 0)
        {
            return sprintf(buf, "%d\n", 0);
        }
        else if (*(virt + dev_data->powerMode) == 1)
        {
            return sprintf(buf, "%d\n", 1);
        }
        else if (*(virt + dev_data->powerMode) == 2)
        {
            return sprintf(buf, "%d\n", 2);
        }
    }

    if (attr == &fanCurve)
    {
        return sprintf(buf, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                       *(virt + dev_data->fanCurve[0]),
                       *(virt + dev_data->fanCurve[1]),
                       *(virt + dev_data->fanCurve[2]),
                       *(virt + dev_data->fanCurve[3]),
                       *(virt + dev_data->fanCurve[4]),
                       *(virt + dev_data->fanCurve[5]),
                       *(virt + dev_data->fanCurve[6]),
                       *(virt + dev_data->fanCurve[7]),
                       *(virt + dev_data->fanCurve[8]),
                       *(virt + dev_data->fanCurve[9]),
                       *(virt + dev_data->fanCurve[10]),
                       *(virt + dev_data->fanCurve[11]),
                       *(virt + dev_data->fanCurve[12]),
                       *(virt + dev_data->fanCurve[13]),
                       *(virt + dev_data->fanCurve[14]),
                       *(virt + dev_data->fanCurve[15]),
                       *(virt + dev_data->fanCurve[16]),
                       *(virt + dev_data->fanCurve[17]),
                       *(virt + dev_data->fanCurve[18]),
                       *(virt + dev_data->fanCurve[19]),
                       *(virt + dev_data->fanCurve[20]),
                       *(virt + dev_data->fanCurve[21]));
    }

    return 0;
}


void writeFanCurve(void)
{
    for (i = 0; i < dev_data->curveLen; i++)
    {
        if (cFanCurve >= 0 && cFanCurve != pFanCurve && cFanCurve <= 45)
        {
            *(virt + dev_data->fanCurve[i]) = cFanCurve;
        }
    }
    cFanCurve = -1;

    pFanCurve = cFanCurve;
}

void writePowerMode(void)
{
    if (cPowerMode >= 0 && cPowerMode != *(virt + dev_data->powerMode) && cPowerMode <= 2)
    {
        *(virt + dev_data->powerMode) = cPowerMode;
    }
    cPowerMode = -1;
}

int init_module(void)
{
    dev_data = &GKCN;
    int error = 0;
    pr_info("Legion Controller %s Loaded \n", LegionControllerVer);
    virt = (ioremap(dev_data->baseEC, 0xFF * 3));
    pr_info("Succefful Mapped EC (Virtual Address 0x%p)\n", virt);

    pr_info("Creating sysfs inteface over /sys/kernel/LegionController/");
    LegionController = kobject_create_and_add("LegionController",
                                              kernel_kobj);
    if (!LegionController)
        return -ENOMEM;

    error = sysfs_create_file(LegionController, &fanSpeedCurrent.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanSpeedCurrent \n");
    }
    error = sysfs_create_file(LegionController, &tempCurrentCPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/tempCurrentCPU \n");
    }
    error = sysfs_create_file(LegionController, &tempCurrentGPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/tempCurrentGPU \n");
    }
    error = sysfs_create_file(LegionController, &fanCurve.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    } /*
    error = sysfs_create_file(LegionController, &fanCurveRight.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }
    error = sysfs_create_file(LegionController, &tempCurveCPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }
    error = sysfs_create_file(LegionController, &tempCurveGPU.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    } */
    error = sysfs_create_file(LegionController, &powerMode.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }

    pr_info("Creating hwmon binding");

    /* A non 0 return means init_module failed; module can't be loaded. */
    return 0;
}

void cleanup_module(void)

{
    kobject_put(LegionController);
    pr_info("Legion Fan %s Unloaded \n", LegionControllerVer);
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("NUTSU7");
MODULE_DESCRIPTION("LEGION");
