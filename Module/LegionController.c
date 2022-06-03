#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/types.h>
#include <asm/io.h>
#include <linux/loop.h>
#include <linux/dmi.h>
#include <linux/delay.h>

#define LegionControllerVer "V0.3"

    struct DEVICE_DATA
{
    uint64_t baseEC;
    uint16_t fanSpeedCurrent;
    uint16_t tempCurrentCPU; // CPU temp
    uint16_t tempCurrentGPU; // GPU temp
    uint16_t fanCurve[22];
    uint16_t fanOffThreshold[6];
    uint8_t fanCurveLen;
    uint8_t fanOffThresholdLen;
    uint8_t powerMode;
};

struct DEVICE_DATA GKCN =
    {
        .baseEC = 0xFE00D400,     // need to start at EC level
        .fanSpeedCurrent = 0x200, // 0x1FC
        .tempCurrentCPU = 0x138,
        .tempCurrentGPU = 0x139,
        .fanCurve = {0x140, 0x141, 0x142, 0x143, 0x144, 0x145, 0x146, 0x147, 0x148, 0x149, 0x14A, 0x150, 0x151, 0x152, 0x153, 0x154, 0x155, 0x156, 0x157, 0x158, 0x159, 0x15A},
        .fanOffThreshold = {0x1C0, 0x1C1, 0x1C2, 0x1D1, 0x1D2, 0x1D3},
        .fanCurveLen = 22,
        .fanOffThresholdLen = 6,
        .powerMode = 0x20,

};

uint8_t *virt;
int i, pFanCurve;

static int cPowerMode = -1;
static int cFanCurve = -1;

module_param(cPowerMode, int, 0644);
module_param(cFanCurve, int, 0644);

struct DEVICE_DATA *biosModel;

static struct kobject *LegionController;
static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);

void writeFanCurve(void);
void writePowerMode(void);
void writeFanOffThreshold(void);

struct kobj_attribute fanSpeedCurrent = __ATTR(fanSpeedCurrent, 0444, sysfs_show, NULL);
struct kobj_attribute tempCurrentCPU = __ATTR(tempCurrentCPU, 0444, sysfs_show, NULL);
struct kobj_attribute tempCurrentGPU = __ATTR(tempCurrentGPU, 0444, sysfs_show, NULL);
struct kobj_attribute fanCurve = __ATTR(fanCurve, 0444, sysfs_show, NULL);
struct kobj_attribute powerMode = __ATTR(powerMode, 0444, sysfs_show, NULL);

static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    if (attr == &fanSpeedCurrent)
    {
        return sprintf(buf, "%d\n", *(virt + biosModel->fanSpeedCurrent));
    }
    if (attr == &tempCurrentCPU)
    {
        return sprintf(buf, "%d\n", *(virt + biosModel->tempCurrentCPU));
    }
    if (attr == &tempCurrentGPU)
    {
        return sprintf(buf, "%d\n", *(virt + biosModel->tempCurrentGPU));
    }

    if (attr == &powerMode)
    {
        writePowerMode();
        
        writeFanCurve();

        
        if (*(virt + biosModel->powerMode) == 0)
        {
            return sprintf(buf, "%d\n", 0);
        }
        else if (*(virt + biosModel->powerMode) == 1)
        {
            return sprintf(buf, "%d\n", 1);
        }
        else if (*(virt + biosModel->powerMode) == 2)
        {
            return sprintf(buf, "%d\n", 2);
        }
    }

    if (attr == &fanCurve)
    {
        return sprintf(buf, "Left: %d %d %d %d %d %d %d %d %d %d %d\nRight: %d %d %d %d %d %d %d %d %d %d %d\n",
                       *(virt + biosModel->fanCurve[0]),
                       *(virt + biosModel->fanCurve[1]),
                       *(virt + biosModel->fanCurve[2]),
                       *(virt + biosModel->fanCurve[3]),
                       *(virt + biosModel->fanCurve[4]),
                       *(virt + biosModel->fanCurve[5]),
                       *(virt + biosModel->fanCurve[6]),
                       *(virt + biosModel->fanCurve[7]),
                       *(virt + biosModel->fanCurve[8]),
                       *(virt + biosModel->fanCurve[9]),
                       *(virt + biosModel->fanCurve[10]),
                       *(virt + biosModel->fanCurve[11]),
                       *(virt + biosModel->fanCurve[12]),
                       *(virt + biosModel->fanCurve[13]),
                       *(virt + biosModel->fanCurve[14]),
                       *(virt + biosModel->fanCurve[15]),
                       *(virt + biosModel->fanCurve[16]),
                       *(virt + biosModel->fanCurve[17]),
                       *(virt + biosModel->fanCurve[18]),
                       *(virt + biosModel->fanCurve[19]),
                       *(virt + biosModel->fanCurve[20]),
                       *(virt + biosModel->fanCurve[21]));
    }

    return 0;
}


void writeFanCurve(void)
{
    for (i = 0; i < biosModel->fanCurveLen; i++)
    {
        if (cFanCurve >= 0 && cFanCurve != pFanCurve && cFanCurve <= 45)
        {
            *(virt + biosModel->fanCurve[i]) = cFanCurve;
        }
    }
    cFanCurve = -1;

    pFanCurve = cFanCurve;
}

void writePowerMode(void)
{
    if (cPowerMode >= 0 && cPowerMode != *(virt + biosModel->powerMode) && cPowerMode <= 2)
    {
        *(virt + biosModel->powerMode) = cPowerMode;
    }
    cPowerMode = -1;
}

void writeFanOffThreshold(void)
{
    for (i = 0; i < biosModel->fanOffThresholdLen; i++)
    {
        *(virt + biosModel->fanOffThreshold[i]) = 0;
    }
}

int init_module(void)
{
    
    //char temp[8];
    //strcpy(temp, dmi_get_system_info(DMI_BIOS_VERSION));
    //temp[4] = '\0';
    //if(strcmp(temp, "GKCN"))
    //{
    //    biosModel = &GKCN;
    //}
    biosModel = &GKCN;
    int error = 0;
    pr_info("Legion Controller %s Loaded \n", LegionControllerVer);
    virt = (ioremap(biosModel->baseEC, 0xFF * 3));
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
    } 
    error = sysfs_create_file(LegionController, &powerMode.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }

    pr_info("Creating hwmon binding");

    /* A non 0 return means init_module failed; module can't be loaded. */
    writeFanOffThreshold();
    return 0;
}

void cleanup_module(void)

{
    int temp = -1;

    if (*(virt + biosModel->powerMode) != 0)
    {
        temp = *(virt + biosModel->powerMode);
        *(virt + biosModel->powerMode) = 0;
        mdelay(1000);
        *(virt + biosModel->powerMode) = temp;
    }
    else
    {
        temp = *(virt + biosModel->powerMode);
        *(virt + biosModel->powerMode) = 1;
        mdelay(1000);
        *(virt + biosModel->powerMode) = temp;
    }

    kobject_put(LegionController);
    pr_info("Legion Fan %s Unloaded \n", LegionControllerVer);
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("NUTSU7 & SMOKELESSCPU");
MODULE_DESCRIPTION("LEGION");
