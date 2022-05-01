#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/types.h>
#include <asm/io.h>

#define LegionControllerVer "V0.3"

struct DEVICE_DATA
{
    //varible meanings- F-Fan  S-Speed T-Temp
    uint64_t baseEC;
    uint16_t fanSpeedCurrentLeft;
    uint16_t fanSpeedCurrentRight;
    uint16_t FTBase_L; 
    uint16_t FTBase_R; 
    uint16_t fanTempCurrentLeft; // CPU temp
    uint16_t fanTempCurrentRight; // GPU temp
    uint16_t fanCurveLeft[9];
    uint16_t fanCurveRight[9];
    uint8_t fanSpeedMultiplier;
    uint8_t powerMode;
};

struct DEVICE_DATA GKCN =
    {
        .baseEC = 0xFE00D400, //need to start at EC level
        .fanSpeedCurrentLeft = 0x200,
        .fanSpeedCurrentRight = 0x201,
        .fanCurveLeft = {0x141, 0x142, 0x143, 0x144, 0x145, 0x146, 0x147, 0x148, 0x149},
        .fanCurveRight = {0x151, 0x152, 0x153, 0x154, 0x155, 0x156, 0x157, 0x158, 0x159},
        .fanSpeedMultiplier = 100,
        .fanTempCurrentLeft = 0x138,
        .fanTempCurrentRight = 0x139,
        .powerMode = 0x20,

};

uint8_t *virt;

static int cPowerMode = -1;
module_param(cPowerMode, int, 0644);

struct DEVICE_DATA *dev_data;

static struct kobject *LegionController;
static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);

struct kobj_attribute fanSpeedCurrentLeft = __ATTR(fanSpeedCurrentLeft, 0444, sysfs_show, NULL);
struct kobj_attribute fanSpeedCurrentRight = __ATTR(fanSpeedCurrentRight, 0444, sysfs_show, NULL);
struct kobj_attribute fanTempCurrentLeft = __ATTR(fanTempCurrentLeft, 0444, sysfs_show, NULL);
struct kobj_attribute fanTempCurrentRight = __ATTR(fanTempCurrentRight, 0444, sysfs_show, NULL);
struct kobj_attribute fanCurveLeft = __ATTR(fanCurveLeft, 0444, sysfs_show, NULL);
struct kobj_attribute fanCurveRight = __ATTR(fanCurveRight, 0444, sysfs_show, NULL);
struct kobj_attribute powerMode = __ATTR(powerMode, 0444, sysfs_show, NULL);


static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    if (attr == &fanSpeedCurrentLeft)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->fanSpeedCurrentLeft) * dev_data->fanSpeedMultiplier);
    }
    if (attr == &fanSpeedCurrentRight)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->fanSpeedCurrentRight) * dev_data->fanSpeedMultiplier);
    }
    if (attr == &fanTempCurrentLeft)
    {
        return sprintf(buf, "%d C\n", *(virt + dev_data->fanTempCurrentLeft));
    }
    if (attr == &fanTempCurrentRight)
    {
        return sprintf(buf, "%d C\n", *(virt + dev_data->fanTempCurrentRight));
    }

    if (attr == &powerMode)
    {
        if (cPowerMode >= 0 && cPowerMode != *(virt + dev_data->powerMode) && cPowerMode <= 2)
        {
            *(virt + dev_data->powerMode) = cPowerMode;
            cPowerMode = -1;
        }

        switch (*(virt + dev_data->powerMode))
        {
        case 0:
            return sprintf(buf, "%s\n", "0");
        case 1:
            return sprintf(buf, "%s\n", "1");
        case 2:
            return sprintf(buf, "%s\n", "2");

        default:
            break;
        }
    }

    if (attr == &fanCurveLeft)
    {
        return sprintf(buf, "%d %d %d %d %d %d %d %d %d\n", 
                       *(virt + dev_data->fanCurveLeft[0]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[1]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[2]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[3]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[4]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[5]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[6]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[7]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveLeft[8]) * dev_data->fanSpeedMultiplier);
    }

    if (attr == &fanCurveRight)
    {
        return sprintf(buf, "%d %d %d %d %d %d %d %d %d\n",
                       *(virt + dev_data->fanCurveRight[0]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[1]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[2]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[3]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[4]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[5]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[6]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[7]) * dev_data->fanSpeedMultiplier,
                       *(virt + dev_data->fanCurveRight[8]) * dev_data->fanSpeedMultiplier);
    }
    return 0;
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

    error = sysfs_create_file(LegionController, &fanSpeedCurrentLeft.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanSpeedCurrentLeft \n");
    }
    error = sysfs_create_file(LegionController, &fanSpeedCurrentRight.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanSpeedCurrentRight \n");
    }
    error = sysfs_create_file(LegionController, &fanTempCurrentLeft.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanTempCurrentLeft \n");
    }
    error = sysfs_create_file(LegionController, &fanTempCurrentRight.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/fanTempCurrentRight \n");
    }
    error = sysfs_create_file(LegionController, &fanCurveLeft.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/powerMode \n");
    }
    error = sysfs_create_file(LegionController, &fanCurveRight.attr);
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
