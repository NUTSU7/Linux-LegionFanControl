#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/types.h>
#include <asm/io.h>

#define LegionControllerVer "V0.3"

uint8_t getPowerMode(void);

struct DEVICE_DATA
{
    //varible meanings- F-Fan  S-Speed T-Temp
    uint64_t EC_Base;
    uint16_t FSBase_L;
    uint16_t FSBase_R;
    uint16_t FSCurrent_L;
    uint16_t FSCurrent_R;
    uint16_t FTBase_L; // CPU temp
    uint16_t FTBase_R; //GPU temp
    uint16_t FTCurrent_L;
    uint16_t FTCurrent_R;
    uint8_t N_Fan_Point[3];
    uint8_t FSMultiplier;
    //uint8_t powerMode;
};

struct DEVICE_DATA GKCN =
    {
        .EC_Base = 0xFE00D520,
        .FSBase_L = 0x21,
        .FSBase_R = 0x31,
        .FSCurrent_L = 0xE0,
        .FSCurrent_R = 0xE1,
        .N_Fan_Point = {9, 9, 10},
        .FSMultiplier = 100,
        .FTCurrent_L = 0x18,
        .FTCurrent_R = 0x19,
        //.powerMode = 0x10,

};

struct DEVICE_DATA *dev_data;
uint8_t *virt;


static struct kobject *LegionController;

static ssize_t sysfs_show(struct kobject *kobj,
                          struct kobj_attribute *attr, char *buf);

struct kobj_attribute FSCurrent_L = __ATTR(FSCurrent_L, 0444, sysfs_show, NULL);
struct kobj_attribute FSCurrent_R = __ATTR(FSCurrent_R, 0444, sysfs_show, NULL);
struct kobj_attribute FTCurrent_L = __ATTR(FTCurrent_L, 0444, sysfs_show, NULL);
struct kobj_attribute FTCurrent_R = __ATTR(FTCurrent_R, 0444, sysfs_show, NULL);
struct kobj_attribute No_of_FanPoint = __ATTR(no_fan_point, 0444, sysfs_show, NULL);
struct kobj_attribute powerMode = __ATTR(powerMode, 0444, sysfs_show, NULL);

static ssize_t sysfs_show(struct kobject *kobj,
                          struct kobj_attribute *attr, char *buf)
{
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
        //return sprintf(buf, "%d\n", *(virt + dev_data->FTCurrent_L) * dev_data);
    }
    if (attr == &FTCurrent_R)
    {
        //return sprintf(buf, "%d\n", *(virt + dev_data->FTCurrent_R) * dev_data);
    }

    if (attr == &powerMode)
    {
        switch (getPowerMode())
        {
        case 12:
            return sprintf(buf, "%s\n", "performance");
        case 13:
            return sprintf(buf, "%s\n", "balanced");
        case 14:
            return sprintf(buf, "%s\n", "quiet");

        default:
            break;
        }
    }
        /* if (attr == &No_of_FanPoint)
    {
        switch (getPowerMode())
        {
        case 0:
            return sprintf(buf, "%d\n", dev_data->N_Fan_Point[3]);
        case 1:
            return sprintf(buf, "%d\n",  dev_data->N_Fan_Point[1]);
        case 2:
            return sprintf(buf, "%d\n",  dev_data->N_Fan_Point[0]);

        default:
            break;
        }
    } */

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
        pr_debug("failed to create the foo file in /sys/kernel/FSCurrent_R \n");
    }
    error = sysfs_create_file(LegionController, &FTCurrent_R.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/FSCurrent_R \n");
    }
    error = sysfs_create_file(LegionController, &powerMode.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/PowerMode \n");
    }
    /* error = sysfs_create_file(LegionController, &No_of_FanPoint.attr);
    if (error)
    {
        pr_debug("failed to create the foo file in /sys/kernel/no_fan_point \n");
    } */
        pr_info("Creating hwmon binding");

    /* A non 0 return means init_module failed; module can't be loaded. */
    return 0;
}

uint8_t getPowerMode(){
    return virt[0x10];
}

void cleanup_module(void)

{
    kobject_put(LegionController);
    pr_info("Legion Fan %s Unloaded \n", LegionControllerVer);
}




MODULE_LICENSE("GPL");
MODULE_AUTHOR("NUTSU7");
MODULE_DESCRIPTION("LEGION");
