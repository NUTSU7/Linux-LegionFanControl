#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/types.h>
#include <asm/io.h>

#define LegionControllerVer "V0.3"

struct DEVICE_DATA
{
    //varible meanings- F-Fan  S-Speed T-Temp
    uint64_t EC_Base;
    uint16_t FSBase_L;
    uint16_t FSBase_R;
    uint16_t FSCurrent_L;
    uint16_t FSCurrent_R;
    uint16_t FTBase_L; 
    uint16_t FTBase_R; 
    uint16_t FTCurrent_L; // CPU temp
    uint16_t FTCurrent_R; // GPU temp
    uint8_t N_Fan_Point[3];
    uint8_t FSMultiplier;
    uint8_t powerMode;
};

struct DEVICE_DATA GKCN =
    {
        .EC_Base = 0xFE00D400, //need to start at EC level
        .FSBase_L = 0x141,
        .FSBase_R = 0x151,
        .FSCurrent_L = 0x200,
        .FSCurrent_R = 0x201,
        .N_Fan_Point = {9, 9, 10},
        .FSMultiplier = 100,
        .FTCurrent_L = 0x138,
        .FTCurrent_R = 0x139,
        .powerMode = 0x20,

};

uint8_t *virt;

static int cPowerMode = -1;
module_param(cPowerMode, int, 0644);

struct DEVICE_DATA *dev_data;

static struct kobject *LegionController;
static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf);

struct kobj_attribute FSBase_L = __ATTR(FSBase_L, 0444, sysfs_show, NULL);
struct kobj_attribute FSBase_R = __ATTR(FSBase_R, 0644, sysfs_show, NULL);
struct kobj_attribute FSCurrent_L = __ATTR(FSCurrent_L, 0444, sysfs_show, NULL);
struct kobj_attribute FSCurrent_R = __ATTR(FSCurrent_R, 0444, sysfs_show, NULL);
struct kobj_attribute FTCurrent_L = __ATTR(FTCurrent_L, 0444, sysfs_show, NULL);
struct kobj_attribute FTCurrent_R = __ATTR(FTCurrent_R, 0444, sysfs_show, NULL);
struct kobj_attribute No_of_FanPoint = __ATTR(no_fan_point, 0644, sysfs_show, NULL);
struct kobj_attribute powerMode = __ATTR(powerMode, 0444, sysfs_show, NULL);


static ssize_t sysfs_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    if (attr == &FSBase_L)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->FSBase_L) * dev_data->FSMultiplier);
    }
    if (attr == &FSBase_R)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->FSBase_R) * dev_data->FSMultiplier);
    }
    if (attr == &FSCurrent_L)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->FSCurrent_L) * dev_data->FSMultiplier);
    }
    if (attr == &FSCurrent_R)
    {
        return sprintf(buf, "%d\n", *(virt + dev_data->FSCurrent_R) * dev_data->FSMultiplier);
    }
    if (attr == &FTCurrent_L)
    {
        return sprintf(buf, "%d C\n", *(virt + dev_data->FTCurrent_L));
    }
    if (attr == &FTCurrent_R)
    {
        return sprintf(buf, "%d C\n", *(virt + dev_data->FTCurrent_R));
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
            return sprintf(buf, "%s\n", "balanced");
        case 1:
            return sprintf(buf, "%s\n", "performance");
        case 2:
            return sprintf(buf, "%s\n", "quiet");

        default:
            break;
        }
    }
    return 0;
}

int init_module(void)
{
    dev_data = &GKCN;
    int error = 0;
    pr_info("Legion Controller %s Loaded \n", LegionControllerVer);
    virt = (ioremap(dev_data->EC_Base, 0xFF * 3));
    pr_info("Succefful Mapped EC (Virtual Address 0x%p)\n", virt);

    pr_info("Creating sysfs inteface over /sys/kernel/LegionController/");
    LegionController = kobject_create_and_add("LegionController",
                                              kernel_kobj);
    if (!LegionController)
        return -ENOMEM;

    error = sysfs_create_file(LegionController, &FSBase_L.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FSBase_L \n");
    }
    error = sysfs_create_file(LegionController, &FSBase_R.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FSBase_R \n");
    }
    error = sysfs_create_file(LegionController, &FSCurrent_L.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FSCurrent_L \n");
    }
    error = sysfs_create_file(LegionController, &FSCurrent_R.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FSCurrent_R \n");
    }
    error = sysfs_create_file(LegionController, &FTCurrent_L.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FTCurrent_L \n");
    }
    error = sysfs_create_file(LegionController, &FTCurrent_R.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FTCurrent_R \n");
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
